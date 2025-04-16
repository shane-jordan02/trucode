# A simple test file with some issues

import os

import sys

import time

import numpy  # Unused import



# Check if a number is prime
def is_prime(num):
    if num <= 1:
        return False
    for i in range(2, int(num**0.5) + 1):
        if num % i == 0:
            return False
    return True

# SyntaxError: missing colon
def greet(name):
    print("Hello " + name)

# Proper use of list comprehension
squares = [x**2 for x in range(10) if x % 2 == 0]

# Variable not defined
def double_it(x):
    return x * y  # y is not defined

# Calculate factorial recursively
def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n - 1)

# Logic error: returns wrong sum
def add_numbers(a, b):
    return a - b  # should be a + b

# Inefficient code: nested loops could be optimized
def find_common(a, b):
    result = []
    for i in a:
        for j in b:
            if i == j:
                result.append(i)
    return result

# Style issue: inconsistent indentation
def say_hello():
    print("Hello")
     print("World")  # Extra space causes IndentationError

# Infinite recursion
def countdown(n):
    print(n)
    countdown(n - 1)  # No base case!

# Bad practice: using mutable default argument
def append_item(item, my_list=[]):
    my_list.append(item)
    return my_list
