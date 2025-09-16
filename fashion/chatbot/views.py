from openai import OpenAI
from dotenv import load_dotenv
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import os
from database.models import Product
from utils import get_chat_history, get_bot_reply, extract_filters,query_products,update_chat_history
# Create your views here.

load_dotenv()

client=OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
class ChatBotView(APIView):
    def post(self,request):
        query=request.data.get("query")
        if not query:
            return Response({"error":"Query is required"}, status=400)
        chat_history = get_chat_history(request)
        bot_reply = get_bot_reply(chat_history, query)     
        filters = extract_filters(bot_reply)
        products=query_products(filters)
        update_chat_history(request, query, bot_reply)

        return Response({
            "Reply": bot_reply,
            "products": products
        })