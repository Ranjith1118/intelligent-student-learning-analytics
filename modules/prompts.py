def build_prompt(question, context, style="structured"):
    details = (
        f"Average score: {context.get('average_score', 'not provided')}%; "
        f"attendance: {context.get('attendance_pct', 'not provided')}%; "
        f"assignment submission: {context.get('submission_rate', 'not provided')}%; "
        f"subject: {context.get('subject', 'not provided')}."
    )
    if style == "basic":
        return f"Answer this learning support question: {question}\nContext: {details}"
    if style == "coach":
        return (
            "Role: You are a supportive learning coach. Avoid blame, labels, and assumptions about ability.\n"
            f"Context: {details}\nQuestion: {question}\n"
            "Offer three realistic actions, ask about barriers, and suggest a progress check. "
            "Protect privacy and avoid high-stakes judgments."
        )
    return (
        "Role: You are an educational support assistant.\n"
        f"Context: {details}\nQuestion: {question}\n"
        "Return a supportive summary, three practical next steps, a simple weekly plan, and a progress check. "
        "State uncertainty, avoid stigmatizing labels, and do not infer sensitive traits."
    )

def compare_prompts(question, context):
    return {
        "Basic prompt": build_prompt(question, context, "basic"),
        "Structured prompt": build_prompt(question, context, "structured"),
        "Supportive coach prompt": build_prompt(question, context, "coach"),
    }

def chatbot_answer(question):
    q = question.lower()
    if any(x in q for x in ["study plan", "timetable", "schedule", "time management"]):
        return (
            "Choose two or three priority topics each week. Study in 25–40 minute blocks with short breaks. "
            "Use active recall, spaced revision, and a weekly review. Adjust the plan to what works for you."
        )
    if any(x in q for x in ["exam", "revision", "remember", "memory"]):
        return (
            "List topics by confidence, practise retrieving answers without notes, revisit difficult material over several days, "
            "and review mistakes. Avoid relying only on rereading."
        )
    if any(x in q for x in ["low marks", "low score", "failing", "poor marks"]):
        return (
            "A low score is feedback about the current approach, not a fixed measure of ability. Review missed questions, "
            "identify one or two topic gaps, practise similar questions, and ask a teacher for targeted feedback."
        )
    if any(x in q for x in ["motivat", "stress", "overwhelm", "anxious"]):
        return (
            "Break work into one small next action, set a manageable goal, and take breaks. If stress persists or affects daily life, "
            "consider speaking with a trusted person, teacher, or qualified support professional."
        )
    return (
        "I can help with study planning, revision, time management, assignment habits, and learning strategies. "
        "Tell me your subject, goal, available study time, and main difficulty."
    )
