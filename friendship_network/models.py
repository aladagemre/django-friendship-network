from django.utils.translation import ugettext_lazy as _

from datetime import datetime
from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      RelationshipTo, Relationship, RelationshipFrom,
                      StructuredRel, DateTimeProperty, BooleanProperty)
import pytz


class DummyMeta:
    fields = []


class FriendshipRequest(StructuredRel):
    """Friendship request relationship between two User nodes.
    May include message for user to introduce himself."""
    # TODO: write log and signals
    message = StringProperty()
    created = DateTimeProperty(default=lambda: datetime.now(pytz.utc))
    viewed = DateTimeProperty()

    def __unicode__(self):
        return "User #%d friendship requested #%d" % (self.from_user_id, self.to_user_id)

    def get_sender(self):
        """
        Returns the sender user id
        of the friendship request.
        :return: user_id
        """
        return self.start_node().user_id

    def get_recipient(self):
        """Returns the recipient user id
        of the friendship request.
        :return: user_id
        """
        return self.end_node().user_id

    def mark_viewed(self):
        """Marks the friendship request
        as viewed."""
        self.viewed = datetime.now(pytz.utc)
        self.save()

    def cancel(self):
        """Cancels the friendship request,
        removes the request relation.
        """
        start_node = self.start_node()
        end_node = self.end_node()
        try:
            start_node.friendship_requests.disconnect(end_node)
            self.save()
        except Exception, e:
            self.log.error("Could not delete the request: {0}".format(e))

    def accept(self):
        """Accepts the friendship request and
        establishes friendship.
        """
        start = self.start_node()
        end = self.end_node()
        try:
            start.friends.connect(end)
        except Exception, e:
            self.log.error("Could not accept the friendship: {0}".format(e))
        else:
            self.cancel()
            self.save()

    def reject(self):
        """Cancels the friendship due to
        rejection."""
        self.cancel()


class User(StructuredNode):
    """User nodes to represent django users
    with their user_id, facebook_id."""
    user_id = IntegerProperty(unique_index=True)
    facebook_id = IntegerProperty(unique_index=True)
    friends = Relationship('User', 'friends_with')
    requests = RelationshipTo('User',
                              'friendship_request',
                              model=FriendshipRequest)
    incoming_requests = RelationshipFrom('User',
                                         'friendship_request',
                                         model=FriendshipRequest)

    follows = RelationshipTo('User', 'follows', model=Follow)
    followed_by = RelationshipFrom('User', 'follows', model=Follow)

    bans = RelationshipTo('User', 'bans', model=Ban)
    banned_by = RelationshipFrom('User', 'bans', model=Ban)

    _meta = DummyMeta()

    def __repr__(self):
        return "User {0}".format(self.user_id)

class Friendship(StructuredRel):
    """Friendship Relationship to be established
    between two User nodes."""
    created = DateTimeProperty(default=lambda: datetime.now(pytz.utc))


class FriendshipManager(object):
    @staticmethod
    def get_nodes(*args):
        """(int[,...]) -> tuple
        Returns the nodes corresponding the user ids.
        :return: Node objects.
        """
        nodes = [User.index.get(user_id=user_id) for user_id in args]
        return nodes

    @staticmethod
    def send_friendship_request(from_id, to_id, message):
        """
        Sends friendship request.
        :param from_id: the requester user id.
        :param to_id: the requestee user id.
        :param message: message to introduce yourself.
        :return:
        """
        from_user, to_user = FriendshipManager.get_nodes(from_id, to_id)
        req = from_user.requests.connect(to_user, {'message': message})
        req.save()
        return True

    @staticmethod
    def cancel_friendship_request(from_id, to_id):
        """
        Cancels the friendhip request.
        :param from_id: the requester user id.
        :param to_id: the requestee user id.
        :return:
        """

        from_user, to_user = FriendshipManager.get_nodes(from_id, to_id)
        from_user.requests.disconnect(to_user)
        return True

    @staticmethod
    def get_friends(user_id):
        """
        Returns the user ids of the friends of the given user.
        :param user_id: user_id to get the friends of.
        :return: friends of the given user.
        """
        node = FriendshipManager.get_nodes(user_id)[0]
        return [friend.user_id for friend in node.friends.all()]

    @staticmethod
    def are_friends(user_id1, user_id2):
        """
        Returns if the given two users are friends or not.
        :param user_id1: user 1
        :param user_id2: user 2
        :return: True if they are friends.
        """
        user1, user2 = FriendshipManager.get_nodes(user_id1, user_id2)[0]
        return user1.friends.is_connected(user2)

    @staticmethod
    def add_friend(user_id1, user_id2):
        """
        Establishes the friendship between the given two users.
        :param user_id1: user 1 id
        :param user_id2: user 2 id
        :return: True if successful.
        """
        user1, user2 = FriendshipManager.get_nodes(user_id1, user_id2)[0]
        user1.friends.connect(user2)
        return True

    @staticmethod
    def remove_friend(user_id1, user_id2):
        """
        Removes the friendship between the given two users.
        :param user_id1: user 1 id
        :param user_id2: user 2 id
        :return: True if successful.
        """
        user1, user2 = FriendshipManager.get_nodes(user_id1, user_id2)[0]
        user1.friends.disconnect(user2)
        return True

    # ============ REQUESTS =================

    @staticmethod
    def get_sent_requests(user_id):
        """
        Returns the sent request objects.
        :param user_id: user_id
        :return: sent FriendshipRequest object list
        """
        node = FriendshipManager.get_nodes(user_id)[0]
        rels = [node.requests.relationship(target)
                for target in node.requests.all()]
        return rels

    @staticmethod
    def get_incoming_requests(user_id):
        """
        Returns the incoming request objects.
        :param user_id: user_id
        :return: incoming FriendshipRequest object list.
        """
        node = FriendshipManager.get_nodes(user_id)[0]
        rels = [node.incoming_requests.relationship(target)
                for target in node.incoming_requests.all()]
        return rels

    @staticmethod
    def get_requested_friends(user_id):
        """
        Finds who the user wanted to be friends with.
        :param user_id: requester user.
        :return: requested target users.
        """
        node = FriendshipManager.get_nodes(user_id)[0]
        return node.requests.all()

    @staticmethod
    def get_requesting_friends(user_id):
        """
        Finds who wants to be friends with the user.
        :param user_id: the target user.
        :return: requester (source) users.
        """
        node = FriendshipManager.get_nodes(user_id)[0]
        return node.incoming_requests.all()

    @staticmethod
    def get_unread_incoming_requests(user_id):
        """
        Returns the unread incoming requests.
        :param user_id: user_id.
        :return: unread incoming requests.
        """
        return [req for req in FM.get_incoming_requests(user_id)
                if not req.viewed]

    # =========== COUNTS ====================

    @staticmethod
    def get_incoming_request_count(user_id):
        """
        Returns the number of incoming requests
        for the given user id.
        :param user_id: user_id.
        :return: number of incoming requests
        """
        node = FriendshipManager.get_nodes(user_id)[0]
        return node.incoming_requests.count()

    @staticmethod
    def get_unread_incoming_request_count(user_id):
        """
        Returns the number of unread incoming requests.
        :param user_id: user_id.
        :return: number of unread incoming requests.
        """
        return len(FriendshipManager.get_unread_incoming_requests(user_id))

    @staticmethod
    def get_sent_request_count(user_id):
        """
        Returns the number of sent requests
        for the given user id.
        :param user_id: user_id.
        :return: number of incoming requests
        """
        node = FriendshipManager.get_nodes(user_id)[0]
        return node.requests.count()


class Follow(StructuredRel):
    """Follow Relationship to be established
    between two User nodes."""
    created = DateTimeProperty(default=lambda: datetime.now(pytz.utc))


class FollowManager(object):
    @staticmethod
    def is_following(user_id1, user_id2):
        """
        Returns if the user1 is following user2.
        :param user_id1: user 1
        :param user_id2: user 2
        :return: True user1 follows user2.
        """
        user1, user2 = FriendshipManager.get_nodes(user_id1, user_id2)[0]
        return user1.follows.is_connected(user2)

    @staticmethod
    def get_followers(user_id):
        """
        Returns the follower user ids of the given user.
        :param user_id: person who is being followed
        :return: follower list.
        """
        node = FriendshipManager.get_nodes(user_id)[0]
        return [friend.user_id for friend in node.followed_by.all()]

    @staticmethod
    def get_following(user_id):
        """
        Returns the user list who the given user follows.
        :param user_id: person who follows.
        :return: following (target) list
        """
        node = FriendshipManager.get_nodes(user_id)[0]
        return [friend.user_id for friend in node.follows.all()]

    @staticmethod
    def follow(user_id1, user_id2):
        """
        user1 starts following user2.
        :param user_id1: user 1
        :param user_id2: user 2
        :return: True if successful.
        """
        user1, user2 = FriendshipManager.get_nodes(user_id1, user_id2)[0]
        user1.follows.connect(user2)
        return True

    @staticmethod
    def unfollow(user_id1, user_id2):
        """
        user1 unfollows user2.
        :param user_id1: user 1
        :param user_id2: user 2
        :return: True if successful.
        """
        user1, user2 = FriendshipManager.get_nodes(user_id1, user_id2)[0]
        user1.follows.disconnect(user2)
        return True


class Ban(StructuredRel):
    created = DateTimeProperty(default=lambda: datetime.now(pytz.utc))


class BanManager(object):
    @staticmethod
    def ban(user_id1, user_id2):
        """
        User 1 bans user 2.
        :param user_id1: banner id
        :param user_id2: bannee id
        :return: True if successful.
        """
        user1, user2 = FriendshipManager.get_nodes(user_id1, user_id2)[0]
        user1.bans.connect(user2)
        return True

    @staticmethod
    def unban(user_id1, user_id2):
        """
        User 1 unbans user 2.
        :param user_id1: banner id
        :param user_id2: bannee id
        :return: True if successful.
        """
        user1, user2 = FriendshipManager.get_nodes(user_id1, user_id2)[0]
        user1.bans.disconnect(user2)
        return True


eren = User.index.get(user_id=3)
emre = User.index.get(user_id=2)
jim = User.index.get(user_id=1)

FM = FriendshipManager
