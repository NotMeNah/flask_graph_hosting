from pathlib import Path


class Profile:
    __graph__path=None

    @staticmethod
    def get_graph_path():
        home_path=Path(__file__).parent.parent

        graph_path=home_path.joinpath("data/graph")
        if not graph_path.exists():
            graph_path.mkdir(parents=True,exist_ok=True)

        return graph_path