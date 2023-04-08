import matplotlib.pyplot as plt
from collections import Counter


class ProgressTracker:
    """
    This class creates a stacked bar chart to
    display the to-do list's task progress/actions
    """

    """ Store progress tracker data on creation """
    def __init__(self, data): self.data = data

    def show(self):
        """ Create & open new progress tracker graph/window """

        # Extract months from data
        months = [int(item[1]) for item in self.data]

        # Count number of occurrences of each month
        monthCounts = Counter(months)

        # Create lists of months & counts for plotting
        x = list(monthCounts.keys())
        y = list(monthCounts.values())

        # Map task actions to colors
        colorDict = {"add": "green", "delete": "red", "done": "blue", "undone": "orange"}

        # Count number of occurrences of each action for each month
        monthActionCounts = {month: Counter() for month in x}
        for action, month in self.data:
            monthActionCounts[int(month)][action] += 1

        # Create lists of counts for each action
        addTaskCounts = [monthActionCounts[month]["add"] for month in x]
        deleteTaskCounts = [monthActionCounts[month]["delete"] for month in x]
        doneTaskCounts = [monthActionCounts[month]["done"] for month in x]
        undoneTaskCounts = [monthActionCounts[month]["undone"] for month in x]

        fig, ax = plt.subplots()

        # Create stacked bar chart with updated legend labels
        ax.bar(x, addTaskCounts, color=colorDict["add"], label="Add Task")
        ax.bar(x, deleteTaskCounts, bottom=addTaskCounts, color=colorDict["delete"],
               label="Delete Task")
        ax.bar(x, doneTaskCounts,
               bottom=[a + b for a, b in zip(addTaskCounts, deleteTaskCounts)],
               color=colorDict["done"], label="Mark Done")
        ax.bar(x, undoneTaskCounts, bottom=[a + b + c for a, b, c in
                                            zip(addTaskCounts, deleteTaskCounts,
                                             doneTaskCounts)],
               color=colorDict["undone"], label="Mark Un-Done")

        ax.set_title("To-Do List Progress Tracker")

        # Give x & y labels some distance between their respective axes
        ax.set_xlabel('Month', labelpad=10)
        ax.set_ylabel('Number of Actions', labelpad=10)

        # Set x-axis to display abbreviated months with labels from Jan to Dec
        ax.xaxis.set_major_locator(plt.FixedLocator(range(1, 13)))
        ax.xaxis.set_major_formatter(
            plt.FixedFormatter(['Jan', 'Feb', 'Mar', 'Apr',
                                'May', 'Jun', 'Jul', 'Aug', 'Sep',
                                'Oct', 'Nov', 'Dec']))
        plt.xticks(rotation=90)

        # Add a legend with updated labels
        ax.legend()

        fig.canvas.manager.set_window_title('To-Do List Progress Tracker')
        plt.show()


# Meant for testing purposes
if __name__ == "__main__":

    """Example 1"""
    # data = [["add", "10"],["done", "10"], ["undone", "10"],
    #         ["add", "01"], ["delete", "01"], ["undone", "01"],
    #         ["add", "07"], ["done", "07"], ["undone", "07"],
    #         ["add", "12"], ["delete", "12"], ["undone", "12"]]

    """Example 2"""
    data = [["add", "10"], ["done", "10"], ["undone", "10"],
            ["add", "01"], ["delete", "01"], ["undone", "01"],
            ["add", "07"], ["done", "07"], ["undone", "07"],
            ["add", "12"], ["delete", "12"], ["undone", "12"],
            ["add", "10"], ["delete", "10"], ["done", "10"], ["undone", "10"],
            ["add", "11"], ["delete", "11"], ["delete", "11"], ["add", "11"],
            ["add", "01"], ["delete", "01"], ["done", "01"], ["undone", "01"],
            ["add", "03"], ["delete", "03"], ["done", "03"], ["undone", "03"],
            ["add", "05"], ["delete", "05"], ["done", "05"], ["undone", "05"],
            ["add", "07"], ["delete", "07"], ["done", "07"], ["undone", "07"],
            ["add", "10"], ["delete", "10"], ["done", "10"], ["undone", "10"],
            ["add", "12"], ["delete", "12"], ["done", "12"], ["undone", "12"]]

    """Example 3"""
    # data = [["add", "09"],["done", "01"], ["undone", "02"]]

    """Example 4"""
    # data = []

    progressTracker = ProgressTracker(data)
    progressTracker.show()
