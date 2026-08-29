"""A very small HTTP server."""

from http.server import HTTPServer, SimpleHTTPRequestHandler


def main(host="127.0.0.1", port=8000):
    HTTPServer((host, port), SimpleHTTPRequestHandler).serve_forever()


if __name__ == "__main__":
    main()
