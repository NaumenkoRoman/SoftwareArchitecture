import subprocess

# Replace 'your_script.bat' with the path to your .bat file
# Add your arguments in the list after the script's name

script_path = "..\\scripts\\start_member.bat"
ports = [5701, 5702, 5703]
processes = []
if __name__ == "__main__":
    for port in ports:
        window_title = f"member-{port}"
        cmd_command = f'start "{window_title}" cmd.exe /k "{script_path} {port} member-{port}"'
        proc = subprocess.Popen(cmd_command, shell=True)
        processes.append(proc)

while True:
    command = input("cluster$ ").split(" ")

    if "help" in command:
        print("help          - show this message.")
        print("exit          - exit the console.")
    elif "exit" in command:
        break

for process in processes:
    process.terminate()
