try:
	from Noyo import app
	import unittest

except Exception as e:
	print("Some Modules are missing {} ".format(e))


class Tests(unittest.TestCase):

	# Check if get_all_people response is 200
	def test_get_all_people(self):
		tester = app.test_client(self)
		response = tester.get("/person")
		statusCode = response.status_code
		self.assertEqual(statusCode, 200)

	# Check that content return is application/json
	def test_content(self):
		tester = app.test_client(self)
		response = tester.get("/person")
		self.assertEqual(response.content_type, "application/json")

	# Check that the response is in the valid format. (Only checking first_name for simplicity now)
	def test_response(self):
		tester = app.test_client(self)
		response = tester.get("/person")
		self.assertTrue(b'first_name' in response.data)

if __name__ == "__main__":
	unittest.main()

