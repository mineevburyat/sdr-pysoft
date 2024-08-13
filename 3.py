def mask(string_to_mask: str) -> str:
  count_mask_simbol = len(string_to_mask[0:-4])
  return f"{'#'*count_mask_simbol}{string_to_mask[-4:]}"

string_to_mask = input()
result = mask(string_to_mask)
print(result)