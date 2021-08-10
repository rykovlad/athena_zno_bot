
class UserSettings:

    def __init__(self, list_of_subj, right_answers, total_quetions):
        if list_of_subj is None:
            list_of_subj = []
        self.list_of_subj = list_of_subj

        if right_answers:
            self.right_answers = right_answers
        else:
            self.right_answers = 0

        if total_quetions:
           self.total_quetions = total_quetions
        else:
            self.total_quetions = 0

    def __repr__(self):
        if self.total_quetions:
            return f"about u: \nlist_of_subj = {self.list_of_subj}, \nstore = " \
                   f"{round(100 * int(self.right_answers) / self.total_quetions, 2)}% ({self.right_answers}/{self.total_quetions}) "
        else:
            return f"about u: \nlist_of_subj = {self.list_of_subj}, \nstore = " \
                   f"{round(100 * int(self.right_answers) / 1, 2)}% ({self.right_answers}/{self.total_quetions}) "

    def __str__(self):
        if self.total_quetions:
            return f"about u: \nlist_of_subj = {self.list_of_subj}, \nstore = " \
                   f"{round(100 * int(self.right_answers) / self.total_quetions, 2)}% ({self.right_answers}/{self.total_quetions}) "
        else:
            return f"about u: \nlist_of_subj = {self.list_of_subj}, \nstore = " \
                   f"{round(100 * int(self.right_answers) / 1, 2)}% ({self.right_answers}/{self.total_quetions}) "

    @classmethod
    def list_of_subj_str_to_list(cls, list_of_subj_str):
        if len(list_of_subj_str) == 2:
            return []
        else:
            return list_of_subj_str[1:-1].split(", ")
