import 'package:flutter/material.dart';
import 'services/api_service.dart';

void main() {
  runApp(const CraftelApp());
}

// ============================================================
// APP
// ============================================================

class CraftelApp extends StatelessWidget {
  const CraftelApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Craftel',
      theme: ThemeData(
        useMaterial3: true,
        fontFamily: 'Roboto',
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF8C6239),
        ),
      ),
      home: const AadhaarLoginScreen(),
    );
  }
}

// ============================================================
// SCREEN 1: AADHAAR LOGIN
// ============================================================

class AadhaarLoginScreen extends StatefulWidget {
  const AadhaarLoginScreen({super.key});

  @override
  State<AadhaarLoginScreen> createState() =>
      _AadhaarLoginScreenState();
}

class _AadhaarLoginScreenState
    extends State<AadhaarLoginScreen> {
  bool isHindi = false;
  bool isLoading = false;

  final TextEditingController aadhaarController =
      TextEditingController();

  Future<void> sendOtp() async {
    if (aadhaarController.text.length != 12) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            isHindi
                ? 'कृपया 12 अंकों का आधार नंबर दर्ज करें'
                : 'Please enter a valid 12-digit Aadhaar number',
          ),
        ),
      );
      return;
    }

    FocusManager.instance.primaryFocus?.unfocus();

    setState(() {
      isLoading = true;
    });

    try {
      final result = await ApiService.sendOtp(
        aadhaarController.text,
      );

      if (!mounted) return;

      if (result['success'] == true) {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => OtpScreen(
              isHindi: isHindi,
            ),
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              result['message'] ??
                  'Failed to send OTP',
            ),
          ),
        );
      }
    } catch (e) {
      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            isHindi
                ? 'OTP भेजने में समस्या हुई'
                : 'Unable to send OTP. Please try again.',
          ),
        ),
      );
    }

    if (mounted) {
      setState(() {
        isLoading = false;
      });
    }
  }

  @override
  void dispose() {
    aadhaarController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFFCFBF9),
      resizeToAvoidBottomInset: true,
      body: SafeArea(
        child: SingleChildScrollView(
          keyboardDismissBehavior:
              ScrollViewKeyboardDismissBehavior.onDrag,
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              children: [
                const SizedBox(height: 30),

                // ==================================================
                // LOGO
                // ==================================================

                Image.asset(
                  'assets/craftel_logo.png',
                  height: 150,
                  width: 150,
                ),

                const SizedBox(height: 25),

                // ==================================================
                // LANGUAGE TOGGLE
                // ==================================================

                Align(
                  alignment: Alignment.centerRight,
                  child: Container(
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius:
                          BorderRadius.circular(30),
                      border: Border.all(
                        color: Colors.grey.shade300,
                      ),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        GestureDetector(
                          onTap: () {
                            setState(() {
                              isHindi = false;
                            });
                          },
                          child: Container(
                            padding:
                                const EdgeInsets.symmetric(
                              horizontal: 14,
                              vertical: 8,
                            ),
                            decoration: BoxDecoration(
                              color: !isHindi
                                  ? const Color(0xFF8C6239)
                                  : Colors.transparent,
                              borderRadius:
                                  BorderRadius.circular(30),
                            ),
                            child: Text(
                              'English',
                              style: TextStyle(
                                color: !isHindi
                                    ? Colors.white
                                    : Colors.black87,
                                fontWeight:
                                    FontWeight.w600,
                              ),
                            ),
                          ),
                        ),
                        GestureDetector(
                          onTap: () {
                            setState(() {
                              isHindi = true;
                            });
                          },
                          child: Container(
                            padding:
                                const EdgeInsets.symmetric(
                              horizontal: 14,
                              vertical: 8,
                            ),
                            decoration: BoxDecoration(
                              color: isHindi
                                  ? const Color(0xFF8C6239)
                                  : Colors.transparent,
                              borderRadius:
                                  BorderRadius.circular(30),
                            ),
                            child: Text(
                              'हिंदी',
                              style: TextStyle(
                                color: isHindi
                                    ? Colors.white
                                    : Colors.black87,
                                fontWeight:
                                    FontWeight.w600,
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),

                const SizedBox(height: 35),

                // ==================================================
                // TITLE
                // ==================================================

                Text(
                  isHindi
                      ? 'Craftel में आपका स्वागत है'
                      : 'Welcome to Craftel',
                  style: const TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF3B332E),
                  ),
                  textAlign: TextAlign.center,
                ),

                const SizedBox(height: 10),

                Text(
                  isHindi
                      ? 'आगे बढ़ने के लिए अपना आधार नंबर दर्ज करें'
                      : 'Enter your Aadhaar number to continue',
                  style: TextStyle(
                    fontSize: 15,
                    color: Colors.grey.shade600,
                  ),
                  textAlign: TextAlign.center,
                ),

                const SizedBox(height: 35),

                // ==================================================
                // AADHAAR FIELD
                // ==================================================

                TextField(
                  controller: aadhaarController,
                  keyboardType: TextInputType.number,
                  maxLength: 12,
                  decoration: InputDecoration(
                    counterText: '',
                    labelText: isHindi
                        ? 'आधार नंबर'
                        : 'Aadhaar Number',
                    hintText: 'Enter 12-digit Aadhaar',
                    prefixIcon: const Icon(
                      Icons.credit_card_outlined,
                      color: Color(0xFF8C6239),
                    ),
                    filled: true,
                    fillColor: Colors.white,
                    border: OutlineInputBorder(
                      borderRadius:
                          BorderRadius.circular(14),
                      borderSide: BorderSide(
                        color: Colors.grey.shade300,
                      ),
                    ),
                    focusedBorder:
                        const OutlineInputBorder(
                      borderRadius:
                          BorderRadius.all(
                        Radius.circular(14),
                      ),
                      borderSide: BorderSide(
                        color: Color(0xFF8C6239),
                        width: 2,
                      ),
                    ),
                  ),
                ),

                const SizedBox(height: 25),

                // ==================================================
                // SEND OTP
                // ==================================================

                SizedBox(
                  width: double.infinity,
                  height: 55,
                  child: ElevatedButton(
                    onPressed:
                        isLoading ? null : sendOtp,
                    style: ElevatedButton.styleFrom(
                      backgroundColor:
                          const Color(0xFF8C6239),
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(
                        borderRadius:
                            BorderRadius.circular(14),
                      ),
                    ),
                    child: isLoading
                        ? const SizedBox(
                            height: 22,
                            width: 22,
                            child:
                                CircularProgressIndicator(
                              color: Colors.white,
                              strokeWidth: 2,
                            ),
                          )
                        : Text(
                            isHindi
                                ? 'OTP भेजें'
                                : 'Send OTP',
                            style: const TextStyle(
                              fontSize: 17,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

// ============================================================
// SCREEN 2: OTP
// ============================================================

class OtpScreen extends StatefulWidget {
  final bool isHindi;

  const OtpScreen({
    super.key,
    required this.isHindi,
  });

  @override
  State<OtpScreen> createState() =>
      _OtpScreenState();
}

class _OtpScreenState extends State<OtpScreen> {
  final TextEditingController otpController =
      TextEditingController();

  bool isLoading = false;

  void verifyOtp() {
    if (otpController.text.length != 6) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            widget.isHindi
                ? 'कृपया 6 अंकों का OTP दर्ज करें'
                : 'Please enter a 6-digit OTP',
          ),
        ),
      );
      return;
    }

    FocusManager.instance.primaryFocus?.unfocus();

    setState(() {
      isLoading = true;
    });

    // DEMO OTP VERIFICATION
    // Real backend verification can be connected later.

    Future.delayed(
      const Duration(milliseconds: 700),
      () {
        if (!mounted) return;

        setState(() {
          isLoading = false;
        });

        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (context) =>
                LoginSuccessScreen(
              isHindi: widget.isHindi,
            ),
          ),
        );
      },
    );
  }

  @override
  void dispose() {
    otpController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFFCFBF9),
      resizeToAvoidBottomInset: true,
      body: SafeArea(
        child: SingleChildScrollView(
          keyboardDismissBehavior:
              ScrollViewKeyboardDismissBehavior.onDrag,
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              children: [
                const SizedBox(height: 40),

                // LOGO
                Image.asset(
                  'assets/craftel_logo.png',
                  height: 120,
                  width: 120,
                ),

                const SizedBox(height: 35),

                Text(
                  widget.isHindi
                      ? 'OTP सत्यापन'
                      : 'Verify OTP',
                  style: const TextStyle(
                    fontSize: 27,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF3B332E),
                  ),
                ),

                const SizedBox(height: 10),

                Text(
                  widget.isHindi
                      ? 'आपके पंजीकृत मोबाइल नंबर पर भेजा गया OTP दर्ज करें'
                      : 'Enter the OTP sent to your registered mobile number',
                  style: TextStyle(
                    color: Colors.grey.shade600,
                    fontSize: 15,
                  ),
                  textAlign: TextAlign.center,
                ),

                const SizedBox(height: 35),

                // OTP FIELD
                TextField(
                  controller: otpController,
                  keyboardType:
                      TextInputType.number,
                  maxLength: 6,
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                    fontSize: 24,
                    letterSpacing: 8,
                    fontWeight: FontWeight.bold,
                  ),
                  decoration: InputDecoration(
                    counterText: '',
                    hintText: '------',
                    filled: true,
                    fillColor: Colors.white,
                    border: OutlineInputBorder(
                      borderRadius:
                          BorderRadius.circular(14),
                    ),
                    focusedBorder:
                        const OutlineInputBorder(
                      borderRadius:
                          BorderRadius.all(
                        Radius.circular(14),
                      ),
                      borderSide: BorderSide(
                        color: Color(0xFF8C6239),
                        width: 2,
                      ),
                    ),
                  ),
                ),

                const SizedBox(height: 25),

                // VERIFY
                SizedBox(
                  width: double.infinity,
                  height: 55,
                  child: ElevatedButton(
                    onPressed:
                        isLoading ? null : verifyOtp,
                    style: ElevatedButton.styleFrom(
                      backgroundColor:
                          const Color(0xFF8C6239),
                      foregroundColor:
                          Colors.white,
                      shape:
                          RoundedRectangleBorder(
                        borderRadius:
                            BorderRadius.circular(14),
                      ),
                    ),
                    child: isLoading
                        ? const SizedBox(
                            height: 22,
                            width: 22,
                            child:
                                CircularProgressIndicator(
                              color: Colors.white,
                              strokeWidth: 2,
                            ),
                          )
                        : Text(
                            widget.isHindi
                                ? 'सत्यापित करें'
                                : 'Verify OTP',
                            style:
                                const TextStyle(
                              fontSize: 17,
                              fontWeight:
                                  FontWeight.bold,
                            ),
                          ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

// ============================================================
// SCREEN 3: LOGIN SUCCESS
// ============================================================

class LoginSuccessScreen extends StatelessWidget {
  final bool isHindi;

  const LoginSuccessScreen({
    super.key,
    required this.isHindi,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFFCFBF9),
      body: SafeArea(
        child: Center(
          child: Padding(
            padding:
                const EdgeInsets.all(24),
            child: Column(
              mainAxisAlignment:
                  MainAxisAlignment.center,
              children: [
                Image.asset(
                  'assets/craftel_logo.png',
                  height: 140,
                  width: 140,
                ),

                const SizedBox(height: 30),

                const Icon(
                  Icons.check_circle,
                  color: Colors.green,
                  size: 70,
                ),

                const SizedBox(height: 20),

                Text(
                  isHindi
                      ? 'सत्यापन सफल!'
                      : 'Verification Successful!',
                  style: const TextStyle(
                    fontSize: 27,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF3B332E),
                  ),
                  textAlign: TextAlign.center,
                ),

                const SizedBox(height: 12),

                Text(
                  isHindi
                      ? 'Craftel में आपका स्वागत है'
                      : 'Welcome to Craftel',
                  style: TextStyle(
                    fontSize: 16,
                    color: Colors.grey.shade600,
                  ),
                ),

                const SizedBox(height: 40),

                SizedBox(
                  width: double.infinity,
                  height: 55,
                  child: ElevatedButton(
                    onPressed: () {
                      Navigator.pushReplacement(
                        context,
                        MaterialPageRoute(
                          builder: (context) =>
                              RoleSelectionScreen(
                            isHindi: isHindi,
                          ),
                        ),
                      );
                    },
                    style:
                        ElevatedButton.styleFrom(
                      backgroundColor:
                          const Color(0xFF8C6239),
                      foregroundColor:
                          Colors.white,
                      shape:
                          RoundedRectangleBorder(
                        borderRadius:
                            BorderRadius.circular(14),
                      ),
                    ),
                    child: Text(
                      isHindi
                          ? 'Craftel में आगे बढ़ें'
                          : 'Continue to Craftel',
                      style: const TextStyle(
                        fontSize: 17,
                        fontWeight:
                            FontWeight.bold,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

// ============================================================
// SCREEN 4: ROLE SELECTION
// ============================================================

class RoleSelectionScreen extends StatefulWidget {
  final bool isHindi;

  const RoleSelectionScreen({
    super.key,
    required this.isHindi,
  });

  @override
  State<RoleSelectionScreen> createState() =>
      _RoleSelectionScreenState();
}

class _RoleSelectionScreenState
    extends State<RoleSelectionScreen> {
  String? selectedRole;

  late bool isHindi;

  @override
  void initState() {
    super.initState();
    isHindi = widget.isHindi;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor:
          const Color(0xFFFCFBF9),

      body: SafeArea(
        child: SingleChildScrollView(
          keyboardDismissBehavior:
              ScrollViewKeyboardDismissBehavior.onDrag,

          child: Padding(
            padding:
                const EdgeInsets.all(24),

            child: Column(
              children: [
                const SizedBox(height: 25),

                // ==================================================
                // LOGO
                // ==================================================

                Image.asset(
                  'assets/craftel_logo.png',
                  height: 120,
                  width: 120,
                ),

                const SizedBox(height: 25),

                // ==================================================
                // LANGUAGE TOGGLE
                // ==================================================

                Align(
                  alignment:
                      Alignment.centerRight,

                  child: Container(
                    decoration:
                        BoxDecoration(
                      color: Colors.white,
                      borderRadius:
                          BorderRadius.circular(
                              30),
                      border: Border.all(
                        color:
                            Colors.grey.shade300,
                      ),
                    ),

                    child: Row(
                      mainAxisSize:
                          MainAxisSize.min,

                      children: [
                        GestureDetector(
                          onTap: () {
                            setState(() {
                              isHindi = false;
                            });
                          },

                          child: Container(
                            padding:
                                const EdgeInsets
                                    .symmetric(
                              horizontal: 14,
                              vertical: 8,
                            ),

                            decoration:
                                BoxDecoration(
                              color: !isHindi
                                  ? const Color(
                                      0xFF8C6239)
                                  : Colors
                                      .transparent,

                              borderRadius:
                                  BorderRadius
                                      .circular(
                                          30),
                            ),

                            child: Text(
                              'English',

                              style: TextStyle(
                                color: !isHindi
                                    ? Colors.white
                                    : Colors.black87,

                                fontWeight:
                                    FontWeight.w600,
                              ),
                            ),
                          ),
                        ),

                        GestureDetector(
                          onTap: () {
                            setState(() {
                              isHindi = true;
                            });
                          },

                          child: Container(
                            padding:
                                const EdgeInsets
                                    .symmetric(
                              horizontal: 14,
                              vertical: 8,
                            ),

                            decoration:
                                BoxDecoration(
                              color: isHindi
                                  ? const Color(
                                      0xFF8C6239)
                                  : Colors
                                      .transparent,

                              borderRadius:
                                  BorderRadius
                                      .circular(
                                          30),
                            ),

                            child: Text(
                              'हिंदी',

                              style: TextStyle(
                                color: isHindi
                                    ? Colors.white
                                    : Colors.black87,

                                fontWeight:
                                    FontWeight.w600,
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),

                const SizedBox(height: 35),

                // ==================================================
                // TITLE
                // ==================================================

                Text(
                  isHindi
                      ? 'आप Craftel का उपयोग कैसे करेंगे?'
                      : 'How will you use Craftel?',

                  style: const TextStyle(
                    fontSize: 27,
                    fontWeight:
                        FontWeight.bold,
                    color:
                        Color(0xFF3B332E),
                  ),

                  textAlign:
                      TextAlign.center,
                ),

                const SizedBox(height: 10),

                Text(
                  isHindi
                      ? 'अपनी भूमिका चुनें'
                      : 'Choose your role',

                  style: TextStyle(
                    fontSize: 15,
                    color:
                        Colors.grey.shade600,
                  ),
                ),

                const SizedBox(height: 35),

                // ==================================================
                // BUYER
                // ==================================================

                _roleCard(
                  role: 'buyer',
                  icon:
                      Icons.shopping_bag_outlined,
                  title: isHindi
                      ? 'खरीदार'
                      : 'Buyer',
                  subtitle: isHindi
                      ? 'उत्पाद खोजें और कारीगरों से जुड़ें'
                      : 'Find products and connect with artisans',
                ),

                const SizedBox(height: 16),

                // ==================================================
                // SELLER
                // ==================================================

                _roleCard(
                  role: 'seller',
                  icon:
                      Icons.storefront_outlined,
                  title: isHindi
                      ? 'विक्रेता'
                      : 'Seller',
                  subtitle: isHindi
                      ? 'अपने उत्पाद बेचें और नए खरीदार खोजें'
                      : 'Sell your products and find new buyers',
                ),

                const SizedBox(height: 35),

                // ==================================================
                // NEXT
                // ==================================================

                SizedBox(
                  width: double.infinity,
                  height: 55,

                  child: ElevatedButton(
                    onPressed:
                        selectedRole == null
                            ? null
                            : () {

                                // CLOSE KEYBOARD
                                FocusManager
                                    .instance
                                    .primaryFocus
                                    ?.unfocus();

                                // SELLER
                                if (selectedRole ==
                                    'seller') {
                                  Navigator.push(
                                    context,
                                    MaterialPageRoute(
                                      builder:
                                          (context) =>
                                              const SellerSetupScreen(),
                                    ),
                                  );
                                }

                                // BUYER
                                else if (selectedRole ==
                                    'buyer') {
                                  debugPrint(
                                    'Buyer interface will be connected next.',
                                  );
                                }
                              },

                    style:
                        ElevatedButton
                            .styleFrom(
                      backgroundColor:
                          const Color(
                              0xFF8C6239),

                      disabledBackgroundColor:
                          Colors
                              .grey
                              .shade300,

                      foregroundColor:
                          Colors.white,

                      shape:
                          RoundedRectangleBorder(
                        borderRadius:
                            BorderRadius.circular(
                                14),
                      ),
                    ),

                    child: Row(
                      mainAxisAlignment:
                          MainAxisAlignment
                              .center,

                      children: [
                        Text(
                          isHindi
                              ? 'आगे'
                              : 'Next',

                          style:
                              const TextStyle(
                            fontSize: 17,
                            fontWeight:
                                FontWeight.bold,
                          ),
                        ),

                        const SizedBox(
                            width: 8),

                        const Icon(
                          Icons.arrow_forward,
                        ),
                      ],
                    ),
                  ),
                ),

                const SizedBox(height: 20),
              ],
            ),
          ),
        ),
      ),
    );
  }

  // ============================================================
  // ROLE CARD
  // ============================================================

  Widget _roleCard({
    required String role,
    required IconData icon,
    required String title,
    required String subtitle,
  }) {
    final bool isSelected =
        selectedRole == role;

    return GestureDetector(
      onTap: () {
        setState(() {
          selectedRole = role;
        });
      },

      child: AnimatedContainer(
        duration:
            const Duration(milliseconds: 200),

        width: double.infinity,

        padding:
            const EdgeInsets.all(20),

        decoration:
            BoxDecoration(
          color: isSelected
              ? const Color(0xFFF4ECE4)
              : Colors.white,

          borderRadius:
              BorderRadius.circular(16),

          border: Border.all(
            color: isSelected
                ? const Color(0xFF8C6239)
                : Colors.grey.shade300,

            width:
                isSelected ? 2 : 1,
          ),
        ),

        child: Row(
          children: [
            Container(
              height: 55,
              width: 55,

              decoration:
                  BoxDecoration(
                color: isSelected
                    ? const Color(
                        0xFF8C6239)
                    : const Color(
                        0xFFF4ECE4),

                borderRadius:
                    BorderRadius.circular(
                        14),
              ),

              child: Icon(
                icon,

                color: isSelected
                    ? Colors.white
                    : const Color(
                        0xFF8C6239),

                size: 28,
              ),
            ),

            const SizedBox(width: 16),

            Expanded(
              child: Column(
                crossAxisAlignment:
                    CrossAxisAlignment.start,

                children: [
                  Text(
                    title,

                    style:
                        const TextStyle(
                      fontSize: 18,
                      fontWeight:
                          FontWeight.bold,
                      color:
                          Color(0xFF3B332E),
                    ),
                  ),

                  const SizedBox(height: 5),

                  Text(
                    subtitle,

                    style: TextStyle(
                      fontSize: 13,
                      color:
                          Colors.grey.shade600,
                    ),
                  ),
                ],
              ),
            ),

            if (isSelected)
              const Icon(
                Icons.check_circle,
                color:
                    Color(0xFF8C6239),
                size: 25,
              ),
          ],
        ),
      ),
    );
  }
}

// ============================================================
// SCREEN 5: SELLER SETUP
// ============================================================

class SellerSetupScreen extends StatefulWidget {
  const SellerSetupScreen({super.key});

  @override
  State<SellerSetupScreen> createState() =>
      _SellerSetupScreenState();
}

class _SellerSetupScreenState
    extends State<SellerSetupScreen> {

  String? selectedLanguage;
  String? selectedState;

  final TextEditingController districtController =
      TextEditingController();

  final TextEditingController mandalController =
      TextEditingController();

  // ============================================================
  // SIX LANGUAGES
  // ============================================================

  final List<String> languages = [
    'English',
    'हिंदी',
    'తెలుగు',
    'தமிழ்',
    'മലയാളം',
    'ಕನ್ನಡ',
  ];

  // ============================================================
  // 26 STATES
  // ============================================================

  final List<String> states = [
    'Andhra Pradesh',
    'Arunachal Pradesh',
    'Assam',
    'Bihar',
    'Chhattisgarh',
    'Goa',
    'Gujarat',
    'Haryana',
    'Himachal Pradesh',
    'Jharkhand',
    'Karnataka',
    'Kerala',
    'Madhya Pradesh',
    'Maharashtra',
    'Manipur',
    'Meghalaya',
    'Mizoram',
    'Nagaland',
    'Odisha',
    'Punjab',
    'Rajasthan',
    'Sikkim',
    'Tamil Nadu',
    'Telangana',
    'Tripura',
    'Uttarakhand',
  ];

  // ============================================================
  // CHECK ALL FIELDS
  // ============================================================z

  bool get canContinue {
    return selectedLanguage != null &&
        selectedState != null &&
        districtController.text
            .trim()
            .isNotEmpty &&
        mandalController.text
            .trim()
            .isNotEmpty;
  }

  @override
  void dispose() {
    districtController.dispose();
    mandalController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor:
          const Color(0xFFFCFBF9),

      resizeToAvoidBottomInset: true,

      body: SafeArea(
        child: SingleChildScrollView(
          keyboardDismissBehavior:
              ScrollViewKeyboardDismissBehavior.onDrag,

          child: Padding(
            padding:
                const EdgeInsets.all(24),

            child: Column(
              crossAxisAlignment:
                  CrossAxisAlignment.center,

              children: [
                const SizedBox(height: 15),

                // ==================================================
                // CRAFTEL LOGO
                // ==================================================

                Container(
                  height: 120,
                  width: 120,

                  decoration:
                      BoxDecoration(
                    color: Colors.white,

                    borderRadius:
                        BorderRadius.circular(
                            26),

                    boxShadow: [
                      BoxShadow(
                        color: Colors.black
                            .withValues(
                                alpha: 0.04),
                        blurRadius: 10,
                        spreadRadius: 2,
                      ),
                    ],
                  ),

                  child: ClipRRect(
                    borderRadius:
                        BorderRadius.circular(
                            26),

                    child: Image.asset(
                      'assets/craftel_logo.png',
                      fit: BoxFit.contain,
                    ),
                  ),
                ),

                const SizedBox(height: 25),

                // ==================================================
                // TITLE
                // ==================================================

                const Text(
                  'Seller Setup',

                  style: TextStyle(
                    fontSize: 25,
                    fontWeight:
                        FontWeight.w800,
                    color:
                        Color(0xFF3B332E),
                  ),
                ),

                const SizedBox(height: 8),

                Text(
                  'Set up your seller profile',

                  style: TextStyle(
                    fontSize: 15,
                    color:
                        Colors.grey.shade600,
                    fontWeight:
                        FontWeight.w500,
                  ),
                ),

                const SizedBox(height: 32),

                // ==================================================
                // LANGUAGE TITLE
                // ==================================================

                const Align(
                  alignment:
                      Alignment.centerLeft,

                  child: Text(
                    'Choose your language',

                    style: TextStyle(
                      fontSize: 17,
                      fontWeight:
                          FontWeight.bold,
                      color:
                          Color(0xFF3B332E),
                    ),
                  ),
                ),

                const SizedBox(height: 12),

                // ==================================================
                // LANGUAGE OPTIONS
                // ==================================================

                ...languages.map(
                  (language) {

                    final bool isSelected =
                        selectedLanguage ==
                            language;

                    return GestureDetector(
                      onTap: () {
                        setState(() {
                          selectedLanguage =
                              language;
                        });
                      },

                      child:
                          AnimatedContainer(
                        duration:
                            const Duration(
                          milliseconds: 200,
                        ),

                        width:
                            double.infinity,

                        margin:
                            const EdgeInsets
                                .symmetric(
                          vertical: 5,
                        ),

                        padding:
                            const EdgeInsets
                                .symmetric(
                          horizontal: 18,
                          vertical: 15,
                        ),

                        decoration:
                            BoxDecoration(
                          color: isSelected
                              ? const Color(
                                  0xFFF4ECE4)
                              : Colors.white,

                          borderRadius:
                              BorderRadius
                                  .circular(
                                      12),

                          border:
                              Border.all(
                            color: isSelected
                                ? const Color(
                                    0xFF8C6239)
                                : Colors
                                    .grey
                                    .shade300,

                            width: isSelected
                                ? 2
                                : 1,
                          ),
                        ),

                        child: Row(
                          children: [
                            Icon(
                              Icons.language,

                              size: 24,

                              color: isSelected
                                  ? const Color(
                                      0xFF8C6239)
                                  : Colors
                                      .grey
                                      .shade600,
                            ),

                            const SizedBox(
                                width: 15),

                            Text(
                              language,

                              style:
                                  TextStyle(
                                fontSize: 17,

                                fontWeight:
                                    isSelected
                                        ? FontWeight
                                            .bold
                                        : FontWeight
                                            .w500,

                                color:
                                    const Color(
                                        0xFF3B332E),
                              ),
                            ),

                            const Spacer(),

                            if (isSelected)
                              const Icon(
                                Icons
                                    .check_circle,

                                color:
                                    Color(
                                        0xFF8C6239),

                                size: 24,
                              ),
                          ],
                        ),
                      ),
                    );
                  },
                ),

                const SizedBox(height: 28),

                // ==================================================
                // LOCATION TITLE
                // ==================================================

                const Align(
                  alignment:
                      Alignment.centerLeft,

                  child: Text(
                    'Your location',

                    style: TextStyle(
                      fontSize: 17,
                      fontWeight:
                          FontWeight.bold,
                      color:
                          Color(0xFF3B332E),
                    ),
                  ),
                ),

                const SizedBox(height: 6),

                Align(
                  alignment:
                      Alignment.centerLeft,

                  child: Text(
                    'Enter your state, district and mandal',

                    style: TextStyle(
                      fontSize: 13,
                      color:
                          Colors.grey.shade600,
                    ),
                  ),
                ),

                const SizedBox(height: 14),

                // ==================================================
                // STATE DROPDOWN
                // ==================================================

                DropdownButtonFormField<String>(
                  initialValue:
                      selectedState,

                  isExpanded: true,

                  decoration:
                      InputDecoration(
                    labelText: 'State',

                    prefixIcon:
                        const Icon(
                      Icons
                          .location_on_outlined,

                      color:
                          Color(0xFF8C6239),
                    ),

                    filled: true,

                    fillColor:
                        Colors.white,

                    border:
                        OutlineInputBorder(
                      borderRadius:
                          BorderRadius
                              .circular(
                                  14),

                      borderSide:
                          BorderSide(
                        color: Colors
                            .grey
                            .shade300,
                      ),
                    ),

                    enabledBorder:
                        OutlineInputBorder(
                      borderRadius:
                          BorderRadius
                              .circular(
                                  14),

                      borderSide:
                          BorderSide(
                        color: Colors
                            .grey
                            .shade300,
                      ),
                    ),

                    focusedBorder:
                        OutlineInputBorder(
                      borderRadius:
                          BorderRadius
                              .circular(
                                  14),

                      borderSide:
                          const BorderSide(
                        color:
                            Color(
                                0xFF8C6239),

                        width: 2,
                      ),
                    ),
                  ),

                  items: states.map(
                    (state) {
                      return DropdownMenuItem<
                          String>(
                        value: state,

                        child:
                            Text(state),
                      );
                    },
                  ).toList(),

                  onChanged:
                      (String? value) {
                    setState(() {
                      selectedState =
                          value;
                    });
                  },
                ),

                const SizedBox(height: 14),

                // ==================================================
                // DISTRICT
                // ==================================================

                _textLocationField(
                  controller:
                      districtController,

                  label: 'District',

                  hint:
                      'Enter your district',
                ),

                const SizedBox(height: 14),

                // ==================================================
                // MANDAL
                // ==================================================

                _textLocationField(
                  controller:
                      mandalController,

                  label: 'Mandal',

                  hint:
                      'Enter your mandal',
                ),

                const SizedBox(height: 30),

                // ==================================================
                // CONTINUE
                // ==================================================

                SizedBox(
                  width:
                      double.infinity,

                  height: 58,

                  child:
                      ElevatedButton(

                    onPressed:
                        canContinue
                            ? () {

                                // CLOSE KEYBOARD
                                FocusManager
                                    .instance
                                    .primaryFocus
                                    ?.unfocus();

                                debugPrint(
                                  'Seller language: '
                                  '$selectedLanguage',
                                );

                                debugPrint(
                                  'State: '
                                  '$selectedState',
                                );

                                debugPrint(
                                  'District: '
                                  '${districtController.text}',
                                );

                                debugPrint(
                                  'Mandal: '
                                  '${mandalController.text}',
                                );

                                // Seller Home
                                // will be connected here.
                              }
                            : null,

                    style:
                        ElevatedButton
                            .styleFrom(

                      backgroundColor:
                          const Color(
                              0xFF8C6239),

                      disabledBackgroundColor:
                          Colors
                              .grey
                              .shade300,

                      foregroundColor:
                          Colors.white,

                      shape:
                          RoundedRectangleBorder(
                        borderRadius:
                            BorderRadius.circular(
                                14),
                      ),

                      elevation: 0,
                    ),

                    child: const Row(
                      mainAxisAlignment:
                          MainAxisAlignment
                              .center,

                      children: [
                        Text(
                          'Continue',

                          style:
                              TextStyle(
                            fontSize: 17,
                            fontWeight:
                                FontWeight.bold,
                          ),
                        ),

                        SizedBox(
                            width: 8),

                        Icon(
                          Icons
                              .arrow_forward,
                          size: 21,
                        ),
                      ],
                    ),
                  ),
                ),

                const SizedBox(height: 20),
              ],
            ),
          ),
        ),
      ),
    );
  }

  // ============================================================
  // TEXT LOCATION FIELD
  // ============================================================

  Widget _textLocationField({
    required TextEditingController controller,
    required String label,
    required String hint,
  }) {
    return TextField(
      controller: controller,

      onChanged: (value) {
        setState(() {});
      },

      textCapitalization:
          TextCapitalization.words,

      decoration:
          InputDecoration(
        labelText: label,

        hintText: hint,

        prefixIcon:
            const Icon(
          Icons.location_on_outlined,
          color: Color(0xFF8C6239),
        ),

        filled: true,

        fillColor: Colors.white,

        border:
            OutlineInputBorder(
          borderRadius:
              BorderRadius.circular(14),

          borderSide:
              BorderSide(
            color:
                Colors.grey.shade300,
          ),
        ),

        enabledBorder:
            OutlineInputBorder(
          borderRadius:
              BorderRadius.circular(14),

          borderSide:
              BorderSide(
            color:
                Colors.grey.shade300,
          ),
        ),

        focusedBorder:
            OutlineInputBorder(
          borderRadius:
              BorderRadius.circular(14),

          borderSide:
              const BorderSide(
            color:
                Color(0xFF8C6239),
            width: 2,
          ),
        ),
      ),
    );
  }
}