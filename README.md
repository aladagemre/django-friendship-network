django-friendship-network
=========================

Django Friendship module that works on Neo4j. You need to have a Neo4j instance running.

Requirements
-------------
Django >= 1.4
neomodel
pytz


Usage
======
Add ``friendship_network`` to ``INSTALLED_APPS``.

To use ``django-friendship`` in your views::

    from django.contrib.auth.models import User
    from friendship_network.models import FriendshipManager, FollowManager

    def my_view(request):
        # List of this user's friends
        all_friends = FriendshipManager.get_friends(request.user.pk)

        # List all unread friendship requests
        requests = FriendshipManager.get_unread_incoming_requests(request.user.pk)

        # List all sent friendship requests
        requests = FriendshipManager.get_sent_requests(request.user.pk)

        # List of this user's followers
        all_followers = FollowManager.get_followers(request.user.pk)

        # List of who this user is following
        following = FollowManager.get_following(request.user.pk)

        ### Managing friendship relationships
        other_user = User.objects.get(pk=1)
        successful = FriendshipManager.send_friendship_request(
                                      request.user.pk, other_user.pk)
        
        new_relationship = FriendshipManager.add_friend(request.user.pk, other_user.pk)
        FriendshipManager.are_friends(request.user.pk, other_user.pk)
        FriendshipManager.remove_friend(other_user.pk, request.user.pk)

        # Create request.user follows other_user relationship
        following_created = FollowManager.follow(request.user.pk, other_user.pk)
