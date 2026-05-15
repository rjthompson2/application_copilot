from job_database.database import get_history
import asyncio

async def show_history(job = '', title = ''):
    values =  await get_history()
    displays = [job[1:3] for job in values]

    if job == '' and title == '':
        for i, display in enumerate(displays):
            print(i+1, " | ".join(display))
        choice = input("Enter job and company to view the description, or the enumeration value, type 'exit' to leave: ")
        if choice.lower() == 'exit':
            return
        if "|" in choice:
            title, job = choice.split(" | ")
        else:
            title = choice
            job = choice
    
    if title.isdigit():
        i = int(title) - 1
        print(" | ".join(displays[i]))
        print(values[i][4])
        return

    
    for i, display in enumerate(displays):
        hits = []
        if display[1] == job or display[1] == title:
            display_value = " | ".join(display)
            if display[1] == job and display[1] == title:
                print(i, display_value)
                print(values[i][4])
                return
            hits.append(i)
    if len(hits) == 1:
        i = hits[0]
        print(" | ".join(displays[i]))
        print(values[i][4])
        return

    print("Please be more specific, there were multiple hits for the inputted search value.")
    return await show_history()


asyncio.run(show_history())