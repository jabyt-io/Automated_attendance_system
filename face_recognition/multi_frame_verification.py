from collections import deque, Counter


class MultiFrameVerifier:

    def __init__(self, required_matches=5, window_size=7):
        self.required_matches = required_matches
        self.window_size = window_size
        self.histories = {}

    def reset(self, student_id=None):

        if student_id is None:
            self.histories.clear()
        else:
            self.histories.pop(student_id, None)

    def update(self, student_id):

        if student_id is None or student_id == "Unknown":
            return None

        if student_id not in self.histories:
            self.histories[student_id] = deque(
                maxlen=self.window_size
            )

        history = self.histories[student_id]
        history.append(student_id)

        counts = Counter(history)
        best_id, count = counts.most_common(1)[0]

        if count >= self.required_matches:
            return best_id

        return None