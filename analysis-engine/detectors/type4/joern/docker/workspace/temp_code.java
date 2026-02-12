
public List<Integer> filterEven(List<Integer> numbers) {
    return numbers.stream()
                  .filter(n -> n % 2 == 0)
                  .collect(Collectors.toList());
}
