#include <iostream>

using namespace ::std;

#include <clang/Format/Format.h>

using namespace ::clang::format;

int main() {
  cout << configurationAsText(getGoogleStyle(FormatStyle::LK_Java)) << endl;
}
