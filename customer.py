import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

worker_password = "totallySecurePassword"  # This is a substitute for an actual password. It is not safe to store a password in code accessible to others, though it helps here for testing purposes.
complaint_list = []

# cred is the key to access the database
cred = credentials.Certificate('/Users/williambelyeu/Documents/practise-b23a4-firebase-adminsdk-qdwuw-5f87d4a08c.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

def add_review(rating, username, complaint):
    # Each review has a few parts. The individual keys are autogenerated, while the rating, username, and complaint must be passed to this function. This function also handles getting the timestamp and saving it to the database.
    doc_ref = db.collection('reviews').document()
    doc_ref.set({
        'rating': rating,
        'username': username,
        'complaint': complaint,
        'timestamp': firestore.SERVER_TIMESTAMP
    })
    print(f"Review added with ID: {doc_ref.id}")

def get_reviews():
    # This will display all reviews and their details, so it is seldom used.
    docs = db.collection('reviews').stream()
    for doc in docs:
        data = doc.to_dict()
        print(f"Document ID: {doc.id}")
        print(f"Rating: {data.get('rating', 'N/A')}")
        print(f"Username: {data.get('username', 'N/A')}")
        print(f"Complaint: {data.get('complaint', 'N/A')}")
        print(f"Timestamp: {data.get('timestamp', 'N/A')}")
        print("----------------------------------")

# Example usage
# add_review(4, "JaneDoe", "The service was slow.")
# get_reviews()

def user_menu():
    role = input("Select role: (1) Customer (2) Worker: ")
    if role == '1':
        make_review()
    elif role == '2':
        password = input("Enter worker password: ")
        if password == worker_password:
            worker_menu()
        else:
            print("Incorrect password.")

def make_review():
    try:
        rating = int(input("Rate the issue (1-5): 1 (irritating), 2 (inconvenient), 3 (dangerous), 4 (illegal), 5 (potentially fatal): "))
        if rating not in range(1, 6):  # Non-numeric entries are also caught in testing.
            print("Invalid rating.")
            return
        username = input("Enter your username: ")  # This could be a simple alias for now; ideally, it would use a login system.
        complaint = input("Describe your complaint: ")  # String, limited to one paragraph for now.
        confirm = input("Submit complaint? (y/n): ")
        if confirm.lower() == 'y':
            add_review(rating, username, complaint)
            print("Review submitted.")
        else:
            print("Submission canceled.")
    except Exception as e:
        print(f"An error occurred: {e}")

def worker_menu():
    while True:
        choice = input("Worker Menu:\n1. Show complaint distribution\n2. Retrieve complaints by rating\n3. View complaint list\n4. Close\nChoice: ")
        if choice == '1':
            show_complaint_distribution()
        elif choice == '2':
            rating_level = int(input("Enter rating level (1-5) to retrieve: "))
            retrieve_complaints_by_rating(rating_level)
        elif choice == '3':
            view_complaint_list()
        elif choice == '4':
            close_program()
            break
        else:
            print("Invalid choice.")

def show_complaint_distribution():
    # Initialize a dictionary to hold counts for each rating level
    distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    # Retrieve all complaints
    docs = db.collection('reviews').stream()
    for doc in docs:
        data = doc.to_dict()
        rating = data.get('rating', None)
        if rating in distribution:
            distribution[rating] += 1
    # Display distribution results
    for rating, count in distribution.items():
        print(f"Rating {rating}: {count} complaints")

def retrieve_complaints_by_rating(rating_level):
    global complaint_list
    docs = db.collection('reviews').where('rating', '==', rating_level).stream()
    for doc in docs:
        complaint = doc.to_dict()
        complaint['id'] = doc.id  # Store document ID to allow deletion if needed
        complaint_list.append(complaint)
        # Remove from the database
        db.collection('reviews').document(doc.id).delete()
    print(f"Retrieved complaints with rating {rating_level}.")

def view_complaint_list():
    global complaint_list
    index = 0
    while index < len(complaint_list):
        complaint = complaint_list[index]
        print(f"Rating: {complaint['rating']}, Username: {complaint['username']}, Complaint: {complaint['complaint']}")
        choice = input("Options: (d)elete, (n)ext, (q)uit: ").lower()
        if choice == 'd':
            del complaint_list[index]
            print("Complaint deleted.")
        elif choice == 'n':
            index += 1
        elif choice == 'q':
            break
        else:
            print("Invalid option.")

def close_program():
    global complaint_list
    for complaint in complaint_list:
        doc_ref = db.collection('reviews').document()
        doc_ref.set({
            'rating': complaint['rating'],
            'username': complaint['username'],
            'complaint': complaint['complaint'],
            'timestamp': complaint.get('timestamp', firestore.SERVER_TIMESTAMP)
        })
    complaint_list.clear()
    print("All complaints re-uploaded and list cleared. Program closed.")

# Start menu
user_menu()