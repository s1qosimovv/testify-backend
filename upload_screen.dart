import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import '../../core/theme/app_theme.dart';
import '../../state/quiz_provider.dart';
import '../widgets/ai_orb.dart';
import '../widgets/mesh_background.dart';
import 'dart:ui';

class UploadScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: MeshBackground(
        child: SafeArea(
          child: Consumer<QuizProvider>(
            builder: (context, provider, child) {
              return LayoutBuilder(
                builder: (context, constraints) {
                  return SingleChildScrollView(
                    child: ConstrainedBox(
                      constraints: BoxConstraints(minHeight: constraints.maxHeight),
                      child: Padding(
                        padding: EdgeInsets.all(MediaQuery.of(context).size.width > 600 ? 32.0 : 20.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            // Top Content: Logo and Title
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const SizedBox(height: 10),
                                // Branded Logo - Explicitly Aligned Left
                                Align(
                                  alignment: Alignment.centerLeft,
                                  child: ClipRRect(
                                    borderRadius: BorderRadius.circular(12),
                                    child: Image.asset(
                                      'assets/images/logo.png',
                                      height: 120, // Adjusted for better balance
                                      fit: BoxFit.contain,
                                    ),
                                  ),
                                ),
                                const SizedBox(height: 32),
                                Text(
                                  "Bilimingizni testga\naylantiring",
                                  style: AppTheme.heading1.copyWith(
                                    fontSize: constraints.maxHeight < 600 ? 28 : 32,
                                    height: 1.2,
                                    fontWeight: FontWeight.w800,
                                  ),
                                ),
                                const SizedBox(height: 8),
                                Text(
                                  "Hujjatni tashlang. AI qolganini qiladi.",
                                  style: AppTheme.bodyMedium.copyWith(
                                    fontSize: 14,
                                    color: AppTheme.textSecondary,
                                  ),
                                ),
                              ],
                            ),

                            const SizedBox(height: 32),

                            // Middle Content: Drop Zone and Selector
                            Column(
                              children: [
                                _buildImmersiveDropZone(context, provider),
                                if (provider.selectedFile != null) ...[
                                  const SizedBox(height: 20),
                                  _buildQuestionCountSelector(context, provider),
                                  const SizedBox(height: 16),
                                  _buildTimeSelector(context, provider),
                                ],
                              ],
                            ),

                            const SizedBox(height: 32),

                            // Bottom Content: Start Button
                            Column(
                              children: [
                                if (provider.error != null) _buildErrorCard(provider.error!),
                                const SizedBox(height: 16),
                                _buildStartButton(context, provider),
                                const SizedBox(height: 10),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ),
                  );
                },
              );
            },
          ),
        ),
      ),
    );
  }

  Widget _buildErrorCard(String error) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: AppTheme.glassDecoration(
        borderRadius: 16,
        borderColor: AppTheme.energyPink.withOpacity(0.5),
      ),
      child: Row(
        children: [
          const Icon(Icons.error_outline_rounded, color: AppTheme.energyPink),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              error,
              style: AppTheme.bodySmall.copyWith(color: AppTheme.energyPink, fontWeight: FontWeight.w600),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildImmersiveDropZone(BuildContext context, QuizProvider provider) {
    final hasFile = provider.selectedFile != null;
    
    return ClipRRect(
      borderRadius: BorderRadius.circular(30),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 15, sigmaY: 15),
        child: InkWell(
          onTap: () => provider.pickFile(),
          borderRadius: BorderRadius.circular(30),
          child: Container(
            height: 180,
            decoration: BoxDecoration(
              color: AppTheme.glassSurface,
              borderRadius: BorderRadius.circular(30),
              border: Border.all(
                color: hasFile ? AppTheme.primaryCyan : AppTheme.glassBorder,
                width: 2,
              ),
              boxShadow: hasFile ? [
                BoxShadow(
                  color: AppTheme.primaryCyan.withOpacity(0.2),
                  blurRadius: 20,
                  spreadRadius: 2,
                )
              ] : null,
            ),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  hasFile ? Icons.description_rounded : Icons.add_circle_outline_rounded,
                  size: 48,
                  color: hasFile ? AppTheme.primaryCyan : AppTheme.textSecondary,
                ),
                const SizedBox(height: 16),
                Text(
                  hasFile ? provider.selectedFile!.name : "Faylni tanlang yoki tashlang",
                  style: AppTheme.bodyLarge.copyWith(
                    fontWeight: FontWeight.w600,
                    color: hasFile ? AppTheme.primaryCyan : AppTheme.textPrimary,
                  ),
                ),
                if (!hasFile) ...[
                   const SizedBox(height: 8),
                   Text(
                    "PDF, DOCX, TXT • Max 10MB",
                    style: AppTheme.bodyMedium,
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildQuestionCountSelector(BuildContext context, QuizProvider provider) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: AppTheme.glassDecoration(
        borderRadius: 20,
        borderColor: AppTheme.primaryBlue.withOpacity(0.3),
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                "Savollar soni",
                style: AppTheme.bodyLarge.copyWith(fontWeight: FontWeight.w600, fontSize: 16),
              ),
              Container(
                width: 100,
                child: TextField(
                  keyboardType: TextInputType.number,
                  inputFormatters: [FilteringTextInputFormatter.digitsOnly],
                  onChanged: (value) {
                    final count = int.tryParse(value);
                    if (count != null) {
                      provider.setQuestionCount(count);
                    }
                  },
                  textAlign: TextAlign.center,
                  style: AppTheme.heading3.copyWith(color: AppTheme.primaryBlue, fontSize: 18),
                  decoration: InputDecoration(
                    hintText: "10",
                    hintStyle: TextStyle(color: AppTheme.textSecondary.withOpacity(0.3)),
                    contentPadding: const EdgeInsets.symmetric(vertical: 8),
                    filled: true,
                    fillColor: AppTheme.primaryBlue.withOpacity(0.1),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide(color: AppTheme.primaryBlue.withOpacity(0.4)),
                    ),
                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide(color: AppTheme.primaryBlue.withOpacity(0.2)),
                    ),
                    focusedBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: const BorderSide(color: AppTheme.primaryBlue, width: 2),
                    ),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            "Maksimum 250 ta savol yaratish mumkin",
            style: AppTheme.bodySmall.copyWith(fontSize: 12, color: AppTheme.textSecondary),
          ),
        ],
      ),
    );
  }

  Widget _buildTimeSelector(BuildContext context, QuizProvider provider) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: AppTheme.glassDecoration(
        borderRadius: 20,
        borderColor: AppTheme.primaryCyan.withOpacity(0.3),
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                "Savollarga vaqt",
                style: AppTheme.bodyLarge.copyWith(fontWeight: FontWeight.w600, fontSize: 16),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                decoration: BoxDecoration(
                  color: AppTheme.primaryCyan.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Text(
                  "${provider.timePerQuestion} sek",
                  style: AppTheme.heading3.copyWith(color: AppTheme.primaryCyan, fontSize: 14),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [15, 30, 45, 60].map((seconds) {
                final isSelected = provider.timePerQuestion == seconds;
                return Padding(
                  padding: const EdgeInsets.only(right: 8.0),
                  child: InkWell(
                    onTap: () => provider.setTimePerQuestion(seconds),
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                      decoration: BoxDecoration(
                        color: isSelected ? AppTheme.primaryCyan : AppTheme.glassSurface,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                          color: isSelected ? AppTheme.primaryCyan : AppTheme.glassBorder,
                        ),
                      ),
                      child: Text(
                        "$seconds s",
                        style: AppTheme.bodySmall.copyWith(
                          color: isSelected ? Colors.black : AppTheme.textPrimary,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ),
                );
              }).toList(),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStartButton(BuildContext context, QuizProvider provider) {
    final canStart = provider.selectedFile != null && !provider.isLoading;

    return Opacity(
      opacity: canStart ? 1.0 : 0.5,
      child: ClipRRect(
        borderRadius: BorderRadius.circular(20),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
          child: InkWell(
            onTap: canStart ? () => provider.startQuizGeneration() : null,
            child: Container(
              padding: const EdgeInsets.symmetric(vertical: 20),
              decoration: AppTheme.glassButtonDecoration(
                gradient: const LinearGradient(
                  colors: [AppTheme.primaryCyan, AppTheme.primaryBlue],
                ),
                borderColor: AppTheme.primaryCyan.withOpacity(0.6),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Text(
                    "Quizni yaratish",
                    style: AppTheme.buttonText,
                  ),
                  const SizedBox(width: 12),
                  Icon(Icons.auto_awesome, color: AppTheme.textPrimary, size: 20),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
