import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  static const String baseUrl =
      'http://172.20.228.131:5000/api/auth';

  static Future<Map<String, dynamic>> sendOtp(
      String aadhaarNumber) async {
    final response = await http.post(
      Uri.parse('$baseUrl/send-otp'),
      headers: {
        'Content-Type': 'application/json',
      },
      body: jsonEncode({
        'aadhaarNumber': aadhaarNumber,
      }),
    );

    return jsonDecode(response.body);
  }

  static Future<Map<String, dynamic>> verifyOtp(
      String otp) async {
    final response = await http.post(
      Uri.parse('$baseUrl/verify-otp'),
      headers: {
        'Content-Type': 'application/json',
      },
      body: jsonEncode({
        'otp': otp,
      }),
    );

    return jsonDecode(response.body);
  }
}