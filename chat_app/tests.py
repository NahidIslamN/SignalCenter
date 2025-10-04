from django.shortcuts import render
from django.views import View

# Create your tests here.

class ChatMessageSocket(View):
    def get(self, request):
        
        return render(self, "messagesocket_test.html")