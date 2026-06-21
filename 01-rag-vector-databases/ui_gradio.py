import gradio as gr
from rag_chain import ask_question

def respond(message, history):
    if not message or message.strip() == "":
        return "", history
    
    try:
        response = ask_question(message)
        history.append((message, response))
        return "", history
    except Exception as e:
        error_msg = f"Sorry, something went wrong: {str(e)}"
        history.append((message, error_msg))
        return "", history


with gr.Blocks(title="Platform Engineering Assistant") as demo:
    gr.Markdown("# 🤖 Platform Engineering Assistant\nRAG System for Platform & Kubernetes Knowledge")
    
    chatbot = gr.Chatbot(height=550)
    msg = gr.Textbox(
        placeholder="Ask any question... (eg: What is Cilium Network Policy?)",
        label="Your Question"
    )
    
    msg.submit(respond, inputs= , outputs= )

demo.launch(share=True)
