// 26 Feb 2015 : GWA : These should work.

int i = maybe("simple_test") 1, 2;
public String test = maybe("another_test") "one","two",   "three";

// 26 Feb 2015 : GWA : These should fail because they are inside comments or
// strings.

/* private bool fail = maybe("not_match") true, false */
// private bool anotherFail = maybe("please_no") true, false
public String test = "maybe (\"again_no\") true, false";

// 26 Feb 2015 : GWA : I guess Java doesn't like single-quoted strings? Who
// knew!

private String another_test = 'maybe (\'please_no\') true, false';

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
