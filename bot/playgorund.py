import docker
import os


client = docker.from_env()


def test_user_code(language: str, file: str, question) -> bool:
    for i in range(0, len(question.answer)):
        answer = question.answer[i]
        input = question.options[i]
        container = client.containers.run(
            image=f"{language}-playground",
            # detach=True,
            network_disabled=True,
            volumes={
                os.path.abspath(file): {
                    "bind": f"/home/user/playground/{file}",
                    "mode": "ro"
                }
            },
            command=f'./playground "{file}" "{input}" "{answer}"',
            stderr=True,
            auto_remove=True,
            # mem_limit="512m"
        )

        if container.decode("utf-8")[:-1] != "True":
            os.remove(file)
            return False

    os.remove(file)
    return True
