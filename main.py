from web_qa import WebQA

domain = "responsive-bootstrap-pandacommerce.netlify.app"
full_url = "https://responsive-bootstrap-pandacommerce.netlify.app/"

if __name__ == '__main__':
    qa = WebQA(domain, full_url)

    question = input("Please ask your question about the website: ")

    ans = qa.answer_question(question=question)

    print(f"The answer to your question is \n{ans}")

