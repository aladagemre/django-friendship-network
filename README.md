django-friendship-network
=========================

Django Friendship module that works on Neo4j. 

You need to have a Neo4j instance running. Tested under neo4j-community-1.9.4-unix.

Why?
-----
Using Graph databases instead of relational databases allows us performing complex graph operations such as friend suggestion and further social network analysis.


Requirements
-------------
* ``Django >= 1.4``
* ``neomodel``
* ``pytz``


Usage
======
Add ``friendship_network`` to ``INSTALLED_APPS``.

To use ``friendship_network`` in your views::

    from django.contrib.auth.models import User
    from friendship_network.models import FriendshipManager, FollowManager

    def my_friendship_view(request):
        # Adding, removing and testing friendship.
        FriendshipManager.add_friend(request.user.pk, other_user.pk)
        FriendshipManager.are_friends(request.user.pk, other_user.pk)
        FriendshipManager.remove_friend(other_user.pk, request.user.pk)
        
        # List of this user's friends
        all_friends = FriendshipManager.get_friends(request.user.pk)

        # Gets unread friendship request count
        unread_count = FriendshipManager.get_unread_incoming_request_count(request.user.pk)
        
        # List all unread friendship requests
        requests = FriendshipManager.get_unread_incoming_requests(request.user.pk)
        
        # List all friendship requests
        requests = FriendshipManager.get_incoming_requests(request.user.pk)
        
        # List all guys who want to be friend with the user.
        requesters = FriendshipManager.get_requesting_friends(request.user.pk)
        
        # List all guys who the user wants to be friend with
        wannabes = FriendshipManager.get_requesting_friends(request.user.pk)
        
        # List all sent friendship requests
        requests = FriendshipManager.get_sent_requests(request.user.pk)


        ### Managing friendship relationships
        other_user = User.objects.get(pk=1)
        successful = FriendshipManager.send_friendship_request(
                                      request.user.pk, other_user.pk)
        
    def my_follow_view(request):
        other_user = User.objects.get(pk=1)
        
        # List of this user's followers
        all_followers = FollowManager.get_followers(request.user.pk)

        # List of who this user is following
        following = FollowManager.get_following(request.user.pk)

        # Create request.user follows other_user relationship
        FollowManager.follow(request.user.pk, other_user.pk)
        
        # Unfollow
        FollowManager.unfollow(request.user.pk, other_user.pk)
        
    def my_ban_view(request):
        # User bans another user.
        BanManager.ban(request.user.pk, other_user.pk)
        
        # User removes ban on another user.
        BanManager.unban(request.user.pk, other_user.pk)
        

TODO
=====
* Friend suggestion
* Hiding banned users.
