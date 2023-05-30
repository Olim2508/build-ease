from auth_app.urls import router
from chats.api.views import MessageViewSet, ConversationViewSet

router.register("messages", MessageViewSet)
router.register("conversations", ConversationViewSet)

urlpatterns = router.urls
