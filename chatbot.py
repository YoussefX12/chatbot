
import requests
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# === CONFIG ===
API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    raise RuntimeError("Missing OPENROUTER_API_KEY environment variable.")OPENROUTER_MODEL = "meta-llama/llama-3-8b-instruct"

# === FIREBASE INIT ===
cred = credentials.Certificate("firebase-adminsdk.json")  # Replace with your file path
firebase_admin.initialize_app(cred)
db = firestore.client()

# === FORMAT DATETIME ===
def format_datetime(value):
    if isinstance(value, datetime):
        return value.strftime("%B %d, %Y at %H:%M")
    return str(value)

# === FORMAT MOVIE ENTRY ===
def format_movie(data):
    return (
        f"Title: {data.get('title', 'Unknown')}\n"
        f"Description: {data.get('description', 'No description.')}\n"
        f"Language: {data.get('language', 'Unknown')}\n"
        f"Genres: {', '.join(data.get('genres', []))}\n"
        f"Duration: {data.get('durationMinutes', 'N/A')} mins\n"
        f"Price: ${data.get('price', 'N/A')}\n"
        f"Screening Time: {format_datetime(data.get('screeningTime'))}\n"
        f"Country: {data.get('country', 'Unknown')}\n"
    )

# === FORMAT CLUB ENTRY ===
def format_club(data):
    events = data.get('events', [])
    social_links = data.get('socialLinks', {})
    tags = data.get('tags', [])
    
    events_str = ", ".join(events) if events else "No upcoming events"
    social_str = ", ".join([f"{k}: {v}" for k,v in social_links.items()]) if social_links else "No social links"
    
    return (
        f"Club Name: {data.get('name', 'Unknown')}\n"
        f"Description: {data.get('description', 'No description.')}\n"
        f"Events: {events_str}\n"
        f"Tags: {', '.join(tags)}\n"
        f"Social Links: {social_str}\n"
    )

# === FORMAT EVENT POST ENTRY ===
def format_event_post(data):
    comments = data.get('comments', [])
    reactions = data.get('reactions', {})
    tags = data.get('tags', [])
    
    comments_str = "\n    - ".join(comments) if comments else "No comments"
    reactions_str = ", ".join([f"{k}: {v}" for k,v in reactions.items()]) if reactions else "No reactions"
    
    return (
        f"Event Post Title: {data.get('title', 'Unknown')}\n"
        f"Club Name: {data.get('clubName', 'N/A')}\n"
        f"Description: {data.get('description', 'No description.')}\n"
        f"Event Date: {format_datetime(data.get('eventDate'))}\n"
        f"Event Type: {data.get('eventType', 'N/A')}\n"
        f"Location: {data.get('location', 'N/A')}\n"
        f"Posted By: {data.get('postedBy', 'N/A')}\n"
        f"Tags: {', '.join(tags)}\n"
        f"Comments:\n    - {comments_str}\n"
        f"Reactions: {reactions_str}\n"
    )

# === FETCH ALL DATA FROM FIREBASE ===
def fetch_all_data():
    # Movies
    movies_ref = db.collection("movies")
    movies = [format_movie(doc.to_dict()) for doc in movies_ref.stream()]

    # Clubs
    clubs_ref = db.collection("clubs")
    clubs = [format_club(doc.to_dict()) for doc in clubs_ref.stream()]

    # Event Posts
    event_posts_ref = db.collection("event_posts")
    event_posts = [format_event_post(doc.to_dict()) for doc in event_posts_ref.stream()]

    # Combine all
    combined = "\n=== MOVIES ===\n" + "\n---\n".join(movies) + "\n\n"
    combined += "=== CLUBS ===\n" + "\n---\n".join(clubs) + "\n\n"
    combined += "=== EVENT POSTS ===\n" + "\n---\n".join(event_posts) + "\n\n"
    
    return combined

# === ASK OPENROUTER ===
def ask_openrouter(question, context):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://yourapp.com",
        "X-Title": "Movie & Club Chatbot"
    }

    messages = [
    {
        "role": "system",
        "content": (
            "You are Mario, a friendly and helpful assistant specialized in providing detailed and accurate information about movies, clubs, and events. "
            "You always respond clearly and politely.\n\n"
            "Your knowledge is strictly limited to the information provided below from the Firebase database. "
            "You do NOT make up any answers or speculate beyond this data.\n\n"
            "Besides answering the user's questions, you proactively suggest related questions or useful tips to enhance the user's experience. "
            "For example, if asked about a movie's screening time, you might also mention the price or genres.\n\n"
            "If the requested information is missing or unclear, respond with: 'Information not available.'\n\n"
            "Be engaging, helpful, and concise.\n\n"
            f"Here is the available data:\n{context}"
        )
    },
    {"role": "user", "content": question}
]


    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json={"model": OPENROUTER_MODEL, "messages": messages}
    )

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        print(f"Error {response.status_code}: {response.text}")
        return "Sorry, there was an error."

# === MAIN LOOP ===
if __name__ == "__main__":
    print("🎬 Movie & Club Bot (Firebase + OpenRouter)")
    context = fetch_all_data()

    print("\n🗂️ Context data loaded:\n")
    print(context[:2000] + "\n... [truncated]\n")  # Print first 2k chars for sanity

    print("Ask me about movies, clubs, or events! Type 'exit' to quit.\n")

    while True:
        question = input("You: ").strip()
        if question.lower() in ["exit", "quit"]:
            break
        answer = ask_openrouter(question, context)
        print(f"Bot: {answer}\n")
