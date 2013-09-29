from django.utils.translation import ugettext_lazy as _

from datetime import datetime
from neomodel import (StructuredNode, StringProperty, IntegerProperty,
    RelationshipTo, Relationship, RelationshipFrom, StructuredRel, DateTimeProperty, BooleanProperty)
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

    follows = RelationshipTo('User', 'follows')

    _meta = DummyMeta()

    def __repr__(self):
        return "User {0}".format(self.user_id)


class Friendship(StructuredRel):
    """Friendship Relationship to be established
    between two User nodes."""
    created = DateTimeProperty(default=lambda: datetime.now(pytz.utc))
    deleted = DateTimeProperty()
    active = BooleanProperty(default=True)


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
        counter = len([req for req in FM.get_incoming_requests(user_id)
                 if not req.viewed])
        return counter

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


eren = User.index.get(user_id=3)
emre = User.index.get(user_id=2)
jim = User.index.get(user_id=1)

FM = FriendshipManager