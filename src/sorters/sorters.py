from src.utils.registro import registro

# ==============================
# 12 ALGORITMOS DE ORDENAMIENTO
# ==============================

def timsort(arr, key):
    return sorted(arr, key=key)


def comb_sort(arr, key):
    arr = arr[:]
    gap = len(arr)
    shrink = 1.3
    sorted_flag = False

    while not sorted_flag:
        gap = int(gap / shrink)
        if gap <= 1:
            gap = 1
            sorted_flag = True
        i = 0
        while i + gap < len(arr):
            if key(arr[i]) > key(arr[i + gap]):
                arr[i], arr[i + gap] = arr[i + gap], arr[i]
                sorted_flag = False
            i += 1
    return arr


def selection_sort(arr, key):
    arr = arr[:]
    for i in range(len(arr)):
        min_idx = i
        for j in range(i + 1, len(arr)):
            if key(arr[j]) < key(arr[min_idx]):
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr


def tree_sort(arr, key):
    class Node:
        def __init__(self, val):
            self.val = val
            self.left = None
            self.right = None

    def insert(root, val):
        if not root:
            return Node(val)
        if key(val) < key(root.val):
            root.left = insert(root.left, val)
        else:
            root.right = insert(root.right, val)
        return root

    def inorder(root, result):
        if root:
            inorder(root.left, result)
            result.append(root.val)
            inorder(root.right, result)

    root = None
    for x in arr:
        root = insert(root, x)
    result = []
    inorder(root, result)
    return result


def pigeonhole_sort(arr, key):
    arr = arr[:]
    keys = [key(x) for x in arr]

    # Normalizar claves a rango pequeño de enteros
    unique_keys = {k: i for i, k in enumerate(sorted(set(keys)))}
    normalized_keys = [unique_keys[k] for k in keys]

    min_key, max_key = min(normalized_keys), max(normalized_keys)
    size = max_key - min_key + 1

    holes = [[] for _ in range(size)]
    for item, nk in zip(arr, normalized_keys):
        holes[nk - min_key].append(item)

    return [x for hole in holes for x in hole]


def bucket_sort(arr, key):
    arr = arr[:]
    max_key = max(key(x) for x in arr)
    size = max_key / len(arr)

    buckets = [[] for _ in range(len(arr))]
    for item in arr:
        idx = int(key(item) / size)
        if idx != len(arr):
            buckets[idx].append(item)
        else:
            buckets[len(arr) - 1].append(item)

    result = []
    for bucket in buckets:
        result.extend(sorted(bucket, key=key))
    return result


def quicksort(arr, key):
    if len(arr) <= 1:
        return arr
    pivot = key(arr[len(arr) // 2])
    left = [x for x in arr if key(x) < pivot]
    middle = [x for x in arr if key(x) == pivot]
    right = [x for x in arr if key(x) > pivot]
    return quicksort(left, key) + middle + quicksort(right, key)

def heapsort(arr, key):
    arr = arr[:]

    def heapify(arr, n, i):
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2

        if left < n and key(arr[left]) > key(arr[largest]):
            largest = left
        if right < n and key(arr[right]) > key(arr[largest]):
            largest = right
        if largest != i:
            arr[i], arr[largest] = arr[largest], arr[i]
            heapify(arr, n, largest)

    n = len(arr)
    # Construir max-heap
    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i)

    # Extraer elementos uno por uno
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]  # mover el mayor al final
        heapify(arr, i, 0)

    return arr

def bitonic_sort(arr, key):
    def comp_and_swap(a, i, j, dire):
        if (dire == 1 and key(a[i]) > key(a[j])) or (dire == 0 and key(a[i]) < key(a[j])):
            a[i], a[j] = a[j], a[i]

    def bitonic_merge(a, low, cnt, dire):
        if cnt > 1:
            k = cnt // 2
            for i in range(low, low + k):
                comp_and_swap(a, i, i + k, dire)
            bitonic_merge(a, low, k, dire)
            bitonic_merge(a, low + k, k, dire)

    def bitonic_sort_rec(a, low, cnt, dire):
        if cnt > 1:
            k = cnt // 2
            bitonic_sort_rec(a, low, k, 1)
            bitonic_sort_rec(a, low + k, k, 0)
            bitonic_merge(a, low, cnt, dire)

    a = arr[:]
    bitonic_sort_rec(a, 0, len(a), 1)
    return a


def gnome_sort(arr, key):
    arr = arr[:]
    index = 0
    while index < len(arr):
        if index == 0 or key(arr[index]) >= key(arr[index - 1]):
            index += 1
        else:
            arr[index], arr[index - 1] = arr[index - 1], arr[index]
            index -= 1
    return arr


def binary_insertion_sort(arr, key):
    arr = arr[:]
    for i in range(1, len(arr)):
        x = arr[i]
        left, right = 0, i - 1
        while left <= right:
            mid = (left + right) // 2
            if key(x) < key(arr[mid]):
                right = mid - 1
            else:
                left = mid + 1
        arr = arr[:left] + [x] + arr[left:i] + arr[i + 1:]
    return arr


def radix_sort(arr, key):
    arr = arr[:]
    max_key = max(key(x) for x in arr)
    exp = 1
    while max_key // exp > 0:
        arr = _counting_sort(arr, exp, key)
        exp *= 10
    return arr


def _counting_sort(arr, exp, key):
    n = len(arr)
    output = [0] * n
    count = [0] * 10

    for i in range(n):
        index = (key(arr[i]) // exp) % 10
        count[index] += 1

    for i in range(1, 10):
        count[i] += count[i - 1]

    i = n - 1
    while i >= 0:
        index = (key(arr[i]) // exp) % 10
        output[count[index] - 1] = arr[i]
        count[index] -= 1
        i -= 1

    return output

algoritmos = {
    "TimSort": timsort,
    "Comb Sort": comb_sort,
    "Selection Sort": selection_sort,
    "Tree Sort": tree_sort,
    "Pigeonhole Sort": pigeonhole_sort,
    "BucketSort": bucket_sort,
    "QuickSort": quicksort,
    "HeapSort": heapsort,
    "Bitonic Sort": bitonic_sort,
    "Gnome Sort": gnome_sort,
    "Binary Insertion Sort": binary_insertion_sort,
    "RadixSort": radix_sort,
}
