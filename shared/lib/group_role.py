class GroupRole:

	owner = "owner"
	manager = "manager"
	user = "user"
	invited = "invited"
	applying = "applying"
	null = "null"   # not in GroupRole.choices

	accept = "accept"
	decline = "decline"

	CHOICES = [owner, manager, user, invited, applying]
	OPERATION_CHOICES = [accept, decline]

	RANKING = [null, applying, invited, user, manager, owner]


	@staticmethod
	def max(role_1, role_2):
		return GroupRole.RANKING[max(GroupRole.RANKING.index(role_1), GroupRole.RANKING.index(role_2))]


	@staticmethod
	def min(role_1, role_2):
		return GroupRole.RANKING[min(GroupRole.RANKING.index(role_1), GroupRole.RANKING.index(role_2))]


	@staticmethod
	def leq(role_1, role_2):
		"""
		Check whether role_1 <= role_2
		"""
		return GroupRole.RANKING.index(role_1) <= GroupRole.RANKING.index(role_2)
