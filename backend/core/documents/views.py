from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated

from .models import Document
from .serializers import DocumentSerializer
from users.permissions import IsAdmin
from analytics.models import ActivityLog
from .ai_search import add_document_to_index, search_documents

import os


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all().order_by("-uploaded_at")
    serializer_class = DocumentSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        if self.action == "create":
            return [IsAdmin()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        file = request.FILES.get("file")

        if not file:
            return Response({"error": "No file provided"}, status=400)

        if not file.name.endswith(".txt"):
            return Response({"error": "Only .txt files allowed"}, status=400)

        content = file.read().decode("utf-8")

        save_dir = os.path.join("media", "documents")
        os.makedirs(save_dir, exist_ok=True)

        save_path = os.path.join(save_dir, file.name)

        with open(save_path, "w", encoding="utf-8") as f:
            f.write(content)

        doc = Document.objects.create(
            title=request.data.get("title", file.name),
            file_path=save_path,
            content=content,
            uploaded_by=request.user,
        )

        try:
            add_document_to_index(doc.id, content)
        except Exception as e:
            print(f"Warning: AI indexing failed: {e}")

        ActivityLog.objects.create(
            user=request.user,
            action="upload",
            detail=f"Uploaded: {doc.title}",
        )

        return Response(DocumentSerializer(doc).data, status=201)


class DocumentSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get("q", "").strip()

        if not query:
            return Response({"error": "Provide ?q=search_term"}, status=400)

        ai_results = search_documents(query, top_k=5)

        results_data = []

        if ai_results:
            doc_ids = [r["doc_id"] for r in ai_results]
            docs_map = {d.id: d for d in Document.objects.filter(id__in=doc_ids)}

            for r in ai_results:
                doc = docs_map.get(r["doc_id"])
                if doc:
                    results_data.append({
                        **DocumentSerializer(doc).data,
                        "relevance_score": round(1 / (1 + r["distance"]), 4),
                    })
        else:
            docs = Document.objects.filter(content__icontains=query)
            results_data = DocumentSerializer(docs, many=True).data

        ActivityLog.objects.create(
            user=request.user,
            action="search",
            detail=query,
        )

        return Response({
            "query": query,
            "count": len(results_data),
            "results": results_data,
        })