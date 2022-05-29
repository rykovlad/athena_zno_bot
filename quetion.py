
class Quetion:
    def __init__(self, data):
        self.question = data[0]
        self.correct_answer = data[1]
        answers = data[2].split(';;;')
        for a in answers:
            a.replace(";", "")
        self.answers = answers

    def __repr__(self):
        return "question = {} \ncorrect_answer = {} \nanswers = {}\n\n".format(self.question, int(self.correct_answer),
                                                                       '; '.join(self.answers))
