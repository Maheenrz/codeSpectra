import os
import random
import csv
import shutil

PROBLEMS = [
    ("two_sum", "Solve for indices i, j in array nums where nums[i] + nums[j] == target."),
    ("reverse_linked_list", "Reverse a singly linked list."),
    ("max_subarray_sum", "Find the contiguous subarray with the largest sum."),
    # Added new problems:
    ("binary_search", "Search for a target value in a sorted array using binary search."),
    ("fibonacci", "Compute the Nth Fibonacci number."),
    ("longest_palindromic_substring", "Find the longest palindromic substring in a given string.")
]

NUM_STUDENTS = 50  # Scaled up for a larger dataset
CLONES_PER_ORIG = 3  # Set higher for more clone variations

DATASET_DIR = "dsa_dataset"
CPP_HEADER = "#include <iostream>\n#include <vector>\n#include <algorithm>\nusing namespace std;\n"

VAR_POOL = [
    ["nums", "numbers", "arr", "vec", "list", "dataset"],
    ["target", "goal", "sum_val", "dest", "threshold"],
    ["i", "idx", "a", "first", "start"],
    ["j", "jdx", "b", "second", "end"],
    ["result", "output", "res", "answer", "solution"]
]

FUNC_TEMPLATE = {
    "two_sum": [
        "vector<int> {FUNC}(vector<int>& {VAR1}, int {VAR2}) {{\n"
        "    for (int {VAR3} = 0; {VAR3} < {VAR1}.size(); ++{VAR3}) {{\n"
        "        for (int {VAR4} = {VAR3}+1; {VAR4} < {VAR1}.size(); ++{VAR4}) {{\n"
        "            if ({VAR1}[{VAR3}] + {VAR1}[{VAR4}] == {VAR2})\n"
        "                return vector<int>{{ {VAR3}, {VAR4} }};\n"
        "        }}\n"
        "    }}\n"
        "    return vector<int>();\n"
        "}}\n"
    ],
    "reverse_linked_list": [
        "struct ListNode {{ int val; ListNode* next; ListNode(int x) : val(x), next(NULL) {{}} }};\n"
        "ListNode* {FUNC}(ListNode* head) {{\n"
        "    ListNode* prev = NULL;\n"
        "    while (head) {{\n"
        "        ListNode* next_node = head->next;\n"
        "        head->next = prev;\n"
        "        prev = head;\n"
        "        head = next_node;\n"
        "    }}\n"
        "    return prev;\n"
        "}}\n"
    ],
    "max_subarray_sum": [
        "int {FUNC}(vector<int>& {VAR1}) {{\n"
        "    int max_sum = {VAR1}[0];\n"
        "    int curr = 0;\n"
        "    for (int num : {VAR1}) {{\n"
        "        curr = max(num, curr+num);\n"
        "        max_sum = max(max_sum, curr);\n"
        "    }}\n"
        "    return max_sum;\n"
        "}}\n"
    ],
    # Templates for the added problems
    "binary_search": [
        "int {FUNC}(vector<int>& {VAR1}, int {VAR2}) {{\n"
        "    int left = 0, right = {VAR1}.size() - 1;\n"
        "    while (left <= right) {{\n"
        "        int mid = left + (right - left) / 2;\n"
        "        if ({VAR1}[mid] == {VAR2}) return mid;\n"
        "        if ({VAR1}[mid] < {VAR2}) left = mid + 1;\n"
        "        else right = mid - 1;\n"
        "    }}\n"
        "    return -1;\n"
        "}}\n"
    ],
    "fibonacci": [
        "int {FUNC}(int {VAR2}) {{\n"
        "    if ({VAR2} <= 1) return {VAR2};\n"
        "    return {FUNC}({VAR2} - 1) + {FUNC}({VAR2} - 2);\n"
        "}}\n"
    ],
    "longest_palindromic_substring": [
        "string {FUNC}(string {VAR1}) {{\n"
        "    int n = {VAR1}.size();\n"
        "    if (n == 0) return \"\";\n"
        "    int start = 0, maxLength = 1;\n"
        "    for (int {VAR3} = 0; {VAR3} < n; ++{VAR3}) {{\n"
        "        // Expand around center\n"
        "    }}\n"
        "    return {VAR1}.substr(start, maxLength);\n"
        "}}\n"
    ]
}

def pick_vars():
    return [random.choice(V) for V in VAR_POOL]

def rand_identifier(base):
    """Generate unique random identifiers."""
    return base + ''.join(random.choices("abcdefghijklmnopqrstuvwxyz", k=random.randint(1, 3)))

def permute_code(code: str):
    """Introduce realistic random variations in the function body by reordering, removing, or adding logic."""
    lines = code.split('\n')
    # Shuffle body lines in random order
    if len(lines) > 5:
        body = lines[1:-2]
        if random.random() < 0.5:  # Random shuffle
            random.shuffle(body)
        lines = [lines[0]] + body + lines[-2:]

        # Additional variability
        if random.random() < 0.4:  # Inject a random comment
            body.insert(random.randint(1, len(body) - 1), "// Temporary variable added for clarity.")
        if random.random() < 0.3:  # Remove a random line
            del body[random.randint(1, len(body) - 1)]

    return '\n'.join(lines)

def write_student_files_and_map():
    """Generate student files for each problem and return file map and unit list."""
    shutil.rmtree(DATASET_DIR, ignore_errors=True)
    os.makedirs(DATASET_DIR, exist_ok=True)
    file_map = {}
    all_units = []

    for prob, desc in PROBLEMS:
        subfolder = os.path.join(DATASET_DIR, prob)
        os.makedirs(subfolder, exist_ok=True)
        file_map[prob] = []
        for student in range(1, NUM_STUDENTS + 1):
            func_name = rand_identifier("solve")
            vars = pick_vars()
            template = FUNC_TEMPLATE[prob][0]
            code = template.format(FUNC=func_name, VAR1=vars[0], VAR2=vars[1], VAR3=vars[2], VAR4=vars[3])
            file_name = f"{prob}_student{student:03d}.cpp"
            file_path = os.path.join(subfolder, file_name)

            code_full = CPP_HEADER + "// " + desc + "\n" + code
            with open(file_path, "w") as f:
                f.write(code_full)
            file_map[prob].append((file_path, [func_name]))
            all_units.append((f"{file_name}:{func_name}", file_name, func_name))

            # Add clones
            for c in range(CLONES_PER_ORIG):
                clone_func_name = func_name + rand_identifier("_clone")
                clone_vars = [v + chr(97 + c) for v in vars]
                clone_code = template.format(FUNC=clone_func_name, VAR1=clone_vars[0], VAR2=clone_vars[1], VAR3=clone_vars[2], VAR4=clone_vars[3])
                clone_code = permute_code(clone_code)
                clone_file_name = f"{prob}_student{student:03d}_clone{c+1}.cpp"
                clone_file_path = os.path.join(subfolder, clone_file_name)
                clone_full = CPP_HEADER + "// CLONE: " + desc + "\n" + clone_code
                with open(clone_file_path, "w") as f:
                    f.write(clone_full)
                file_map[prob].append((clone_file_path, [clone_func_name]))
                all_units.append((f"{clone_file_name}:{clone_func_name}", clone_file_name, clone_func_name))

    return file_map, all_units

def build_positive_pairs(file_map):
    pos_pairs = []
    for prob, files in file_map.items():
        origs = [f for f in files if "clone" not in os.path.basename(f[0])]
        clones = [f for f in files if "clone" in os.path.basename(f[0])]
        for orig in origs:
            orig_fname, orig_funcs = orig
            student_no = orig_fname.split("_student")[-1].split(".")[0]
            for orig_func in orig_funcs:
                for clone in clones:
                    if student_no in clone[0]:
                        for clone_func in clone[1]:
                            pos_pairs.append((f"{os.path.basename(orig_fname)}:{orig_func}",
                                              f"{os.path.basename(clone[0])}:{clone_func}", 1))
    return pos_pairs

def build_negative_pairs(all_units):
    units_by_prob = {}
    for unit_id, fname, func in all_units:
        prob = fname.split('_')[0]
        if prob not in units_by_prob:
            units_by_prob[prob] = []
        units_by_prob[prob].append(unit_id)
    all_probs = list(units_by_prob.keys())
    neg_pairs = set()
    while len(neg_pairs) < 10 * NUM_STUDENTS:  # Dynamic scaling based on data size
        p1, p2 = random.sample(all_probs, 2)
        u1 = random.choice(units_by_prob[p1])
        u2 = random.choice(units_by_prob[p2])
        if u1 != u2:
            neg_pairs.add((u1, u2, 0))
    return list(neg_pairs)

def main():
    file_map, all_units = write_student_files_and_map()
    pos_pairs = build_positive_pairs(file_map)
    neg_pairs = build_negative_pairs(all_units)
    pairs = pos_pairs + neg_pairs
    random.shuffle(pairs)
    # Write pairs CSV
    with open(os.path.join(DATASET_DIR, "pairs.csv"), "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["unitA_id", "unitB_id", "label"])
        for uA, uB, lab in pairs:
            writer.writerow([uA, uB, lab])
    print(f"Generated {len(pairs)} pairs ({len(pos_pairs)} positives, {len(neg_pairs)} negatives).")
    print(f"All files and pairs.csv written to ./{DATASET_DIR}")

if __name__ == "__main__":
    main()