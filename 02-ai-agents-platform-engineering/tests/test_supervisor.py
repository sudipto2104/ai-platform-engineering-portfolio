from platform_agents.supervisor import route_question


def test_routes_kubernetes_questions() -> None:
    assert route_question("Why is my pod CrashLoopBackOff?") == "kubernetes"
    assert route_question("List pods in the default namespace") == "kubernetes"


def test_routes_general_questions_to_search() -> None:
    assert route_question("What is the difference between ArgoCD and Flux?") == "search"