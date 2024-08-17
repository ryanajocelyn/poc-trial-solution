"""
 There is a collection of input strings and a collection of query strings.
 For each query string, determine how many times it occurs in the list of input strings.
 Return an array of the results.

 Example
 strings = ['ab', 'ab', 'abc']
 queries = ['ab', 'abc','bc']

 There are 2 instances of 'ab', 1 of 'abc' and 0 of 'bc'.
 For each query, add an element to the return array,

 results = [2, 1, 0].
"""


def matching_strings(strings, queries):
    match_count = []
    string_counts = {}
    for string in strings:
        string_counts[string] = string_counts.get(string, 0) + 1

    for query in queries:
        match_count.append(string_counts.get(query, 0))

    return match_count


if __name__ == '__main__':
    str_list = ['ab', 'ab', 'abc']
    qry_list = ['ab', 'abc', 'bc']

    results = matching_strings(str_list, qry_list)
    print(results)
