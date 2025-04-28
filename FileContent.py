with open('test.txt', 'r') as file:
    content = file.read()  
content_split=content.split() #這是存成list
n=len(content_split)
print("The number of words in the file is:",n)

number_of_unique_words=len(set(content_split))#獨一無二
print("The number of unique words in the file is:",number_of_unique_words)

def frequency_of_words(content_split):
    frequency = {}
    for word in content_split:
        if word in frequency:
            frequency[word] += 1
        else:
            frequency[word] = 1
    return frequency
frequency = frequency_of_words(content_split)

top_n_words = sorted(frequency.items(), key=lambda x: x[1], reverse=True)[:3]
#items會回傳一個list，list裡面是tuple，tuple裡面是key和value
#reverse=True是從大到小排序，含頭不含尾，所以[:3]是0,1,2

print("The top 3 most frequent words are:")
for word, freq in top_n_words:
    print(f"{word}: {freq}")

