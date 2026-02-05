from ai.rag import SituationRAG


def divider():
    print("\n" + "=" * 40 + "\n")


def main():
    rag = SituationRAG("data/situations.json")

    situation_id = "subway_fire"
    situation = rag.get(situation_id)

    divider()
    print("📦 RAG RETRIEVAL TEST")
    divider()

    print("Situation ID:")
    print(situation["id"])

    divider()
    print("Description:")
    print(situation["description"])

    divider()
    print("Viable survival strategies:")
    for strat in situation["viable_strategies"]:
        print(f"- {strat['description']}")

    divider()
    print("Common failures:")
    for failure in situation["common_failures"]:
        print(f"- {failure}")

    divider()
    print("✅ RAG retrieval successful.")


if __name__ == "__main__":
    main()
