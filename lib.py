def find_block(content, start, delimiter_left, delimiter_right):
  def is_block(string, delimiter_left, delimiter_right):
    return (string.count(delimiter_left) - string.count(delimiter_right) == 0)
  
  assert content[start] == delimiter_left, "Buffer does not start with delimiter."

  search_start = start
  buffer_end = start

  while True:
    buffer_increment = content[search_start:].find(delimiter_right)
    assert buffer_increment != -1, "Unmatched delimiters."
    buffer_end += buffer_increment + 1
    block_buffer = content[start:buffer_end]
    if is_block(block_buffer, delimiter_left, delimiter_right):
      return buffer_end, block_buffer
    else:
      search_start += buffer_increment + 1
