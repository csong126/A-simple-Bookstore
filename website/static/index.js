function deleteBook(ISBN) {
  fetch("/delete_from_cart", {
    method: "POST",
    body: JSON.stringify({ ISBN: ISBN }),
  }).then((_res) => {
    window.location.href = "/";
  });
}
