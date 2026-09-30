from crewai.flow.flow import Flow, start


class TestFlow(Flow):

    @start()
    def hello(self):
        print("CrewAI Flow started!")
        return "success"


if __name__ == "__main__":
    TestFlow().kickoff()