from chat_app import ChatApp

if __name__ == '__main__':
    try:
        server = ChatApp()
        server.run()

    except Exception as e:
        print(e)
