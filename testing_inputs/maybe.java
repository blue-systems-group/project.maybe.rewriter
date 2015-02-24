int i = maybe("simple_test") 1, 2;
public boolean String test = maybe("another_test") "one", "two", "three";

maybe ("block_test") {
  if ("true") {
    i = 0;
  } else {
    j = 0;
  }
} or {
  i = 1;
} or {
  j = 2;
  maybe ("another test") {
    j = 3;
  }
}
