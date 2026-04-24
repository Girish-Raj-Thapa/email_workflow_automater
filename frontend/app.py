import requests
import streamlit as st

API_BASE_URL = "http://127.0.0.1:8000/api/v1"

st.set_page_config(
    page_title="AI Email Workflow Automation",
    page_icon="📧",
    layout="wide",
)

st.title("AI Email Workflow Automation System")
st.caption("Minimal dashboard for processing emails, workflows, and replies.")

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Process Email", "Inbox", "Workflows", "Replies"],
)


def process_email_page():
    st.header("Process Email")
    st.write("Submit an email and automatically run AI analysis, workflow routing, and reply drafting.")

    with st.form("process_email_form"):
        sender_email = st.text_input("Sender Email", value="girish@gmail.com")
        subject = st.text_input("Subject", value="Payment completed but account still locked")
        body = st.text_area(
            "Email Body",
            value="Hi team, I paid $49 for my subscription today, but my account is still locked. The payment email is rahul.sharma@example.com. Please help.",
            height=180,
        )

        submitted = st.form_submit_button("Process Email")

    if submitted:
        payload = {
            "sender_email": sender_email,
            "subject": subject,
            "body": body,
        }

        with st.spinner("Processing email with AI workflow..."):
            response = requests.post(f"{API_BASE_URL}/emails/process", json=payload)

        if response.status_code == 201:
            data = response.json()
            st.success("Email processed successfully.")

            st.subheader("AI Analysis")
            st.json(data["analysis"])

            st.subheader("Workflow Created")
            st.json(data["workflow"])

            st.subheader("Draft Reply")
            st.json(data["reply"])
        else:
            st.error(f"Request failed with status code {response.status_code}")
            st.text(response.text)


def inbox_page():
    st.header("Inbox")
    st.write("View all submitted emails.")

    try:
        response = requests.get(f"{API_BASE_URL}/emails")
    except requests.RequestException as exc:
        st.error(f"Could not connect to backend: {exc}")
        return

    if response.status_code != 200:
        st.error(f"Failed to load emails: {response.status_code}")
        st.text(response.text)
        return

    emails = response.json()

    if not emails:
        st.info("No emails found.")
        return

    for email in emails:
        with st.expander(f"{email['subject']} — {email['processing_status']}"):
            st.write(f"**From:** {email['sender_email']}")
            st.write(f"**Received at:** {email['received_at']}")
            st.write(f"**Email ID:** `{email['id']}`")
            st.write("**Body:**")
            st.write(email["body"])


def workflows_page():
    st.header("Workflows")
    st.write("View routed workflow items and their status.")

    try:
        response = requests.get(f"{API_BASE_URL}/workflows")
    except requests.RequestException as exc:
        st.error(f"Could not connect to backend: {exc}")
        return

    if response.status_code != 200:
        st.error(f"Failed to load workflows: {response.status_code}")
        st.text(response.text)
        return

    workflows = response.json()

    if not workflows:
        st.info("No workflows found.")
        return

    for workflow in workflows:
        title = f"{workflow['workflow_type']} | {workflow['assigned_team']} | {workflow['status']}"

        with st.expander(title):
            st.write(f"**Workflow ID:** `{workflow['id']}`")
            st.write(f"**Email ID:** `{workflow['email_id']}`")
            st.write(f"**Analysis ID:** `{workflow['analysis_id']}`")
            st.write(f"**Priority:** {workflow['priority']}")
            st.write(f"**Status:** {workflow['status']}")
            st.write(f"**Created at:** {workflow['created_at']}")
            st.write(f"**Updated at:** {workflow['updated_at']}")

            st.subheader("Update Status")

            status_options = [
                "open",
                "in_progress",
                "resolved",
                "closed",
                "awaiting_review",
                "escalated",
            ]

            new_status = st.selectbox(
                "New status",
                status_options,
                index=status_options.index(workflow["status"]),
                key=f"status_{workflow['id']}",
            )

            note = st.text_input(
                "Note",
                key=f"note_{workflow['id']}",
                placeholder="Add a short note for the timeline log",
            )

            if st.button("Update Status", key=f"update_{workflow['id']}"):
                payload = {
                    "status": new_status,
                    "note": note if note else None,
                }

                update_response = requests.patch(
                    f"{API_BASE_URL}/workflows/{workflow['id']}/status",
                    json=payload,
                )

                if update_response.status_code == 200:
                    st.success("Workflow status updated.")
                    st.rerun()
                else:
                    st.error(f"Failed to update status: {update_response.status_code}")
                    st.text(update_response.text)

            detail_response = requests.get(f"{API_BASE_URL}/workflows/{workflow['id']}")

            if detail_response.status_code == 200:
                detail = detail_response.json()
                st.subheader("Timeline Logs")

                for log in detail.get("logs", []):
                    st.write(f"**{log['step']}**")
                    st.caption(log["created_at"])
                    st.write(log["details"])
                    st.divider()
            else:
                st.warning("Could not load workflow logs.")


def replies_page():
    st.header("Replies")
    st.write("View drafted simulated replies generated by the AI workflow.")

    try:
        response = requests.get(f"{API_BASE_URL}/replies")
    except requests.RequestException as exc:
        st.error(f"Could not connect to backend: {exc}")
        return

    if response.status_code != 200:
        st.error(f"Failed to load replies: {response.status_code}")
        st.text(response.text)
        return

    replies = response.json()

    if not replies:
        st.info("No replies found.")
        return

    for reply in replies:
        with st.expander(f"{reply['reply_subject']} — {reply['status']}"):
            st.write(f"**Reply ID:** `{reply['id']}`")
            st.write(f"**Email ID:** `{reply['email_id']}`")
            st.write(f"**Analysis ID:** `{reply['analysis_id']}`")
            st.write(f"**Status:** {reply['status']}")
            st.write(f"**Created at:** {reply['created_at']}")
            st.write("**Reply Body:**")
            st.write(reply["reply_body"])


if page == "Process Email":
    process_email_page()
elif page == "Inbox":
    inbox_page()
elif page == "Workflows":
    workflows_page()
elif page == "Replies":
    replies_page()
