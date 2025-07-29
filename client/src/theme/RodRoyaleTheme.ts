// Rod Royale Theme - Playful, competitive fishing/battle royale aesthetic
export const RodRoyaleTheme = {
  colors: {
    // Primary brand colors
    primary: '#21588D',        // Deep blue (shield fill)
    primaryDark: '#10284F',    // Dark navy (shield outline)
    secondary: '#F8B400',      // Mustard yellow (main text)
    secondaryDark: '#E6A500',  // Darker yellow for pressed states
    
    // Background colors
    background: '#4DB6E8',     // Sky blue
    backgroundLight: '#E6F3FF', // Light blue tint
    surface: '#FFFFFF',        // White (clouds)
    surfaceElevated: '#F8FBFF', // Slightly tinted white
    
    // Text colors
    text: '#1B1D34',          // Charcoal navy (text outline)
    textSecondary: '#666666',  // Medium gray
    textLight: '#FFFFFF',      // White text
    textAccent: '#F8B400',     // Yellow accent text
    
    // Nature-inspired accents
    success: '#2E7D32',        // Forest green (fish body)
    successLight: '#CDE3D1',   // Light gray-green (fish belly)
    warning: '#F8B400',        // Mustard yellow
    error: '#D32F2F',          // Red for errors
    
    // Interactive elements
    interactive: '#21588D',    // Deep blue
    interactiveHover: '#1A4A7A', // Darker blue
    interactivePressed: '#144066', // Even darker blue
    
    // Utility colors
    border: '#E0E0E0',         // Light gray borders
    borderDark: '#10284F',     // Dark navy borders
    disabled: '#BDBDBD',       // Gray for disabled states
    overlay: 'rgba(27, 29, 52, 0.7)', // Dark overlay
    
    // Special accent colors
    bronze: '#8C4E28',         // Mahogany brown (rod handle)
    silver: '#C0C0C0',         // Silver gray (hook)
  },
  
  // Typography with bold, playful fonts
  typography: {
    // Main headings - bold and competitive
    h1: {
      fontSize: 32,
      fontWeight: 'bold' as const,
      color: '#F8B400', // Mustard yellow
      textShadowColor: '#1B1D34',
      textShadowOffset: { width: 2, height: 2 },
      textShadowRadius: 4,
    },
    h2: {
      fontSize: 24,
      fontWeight: 'bold' as const,
      color: '#21588D', // Deep blue
    },
    h3: {
      fontSize: 20,
      fontWeight: 'bold' as const,
      color: '#10284F', // Dark navy
    },
    
    // Body text
    body: {
      fontSize: 16,
      fontWeight: '400' as const,
      color: '#1B1D34', // Charcoal navy
    },
    bodySecondary: {
      fontSize: 14,
      color: '#666666',
    },
    
    // Special text styles
    accent: {
      fontSize: 16,
      fontWeight: 'bold' as const,
      color: '#F8B400', // Mustard yellow
    },
    competitive: {
      fontSize: 18,
      fontWeight: 'bold' as const,
      color: '#2E7D32', // Forest green
      textTransform: 'uppercase' as const,
    },
  },
  
  // Spacing system
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
    xxl: 48,
  },
  
  // Border radius for that game-like feel
  borderRadius: {
    sm: 8,
    md: 12,
    lg: 16,
    xl: 24,
    round: 50,
  },
  
  // Shadows for depth
  shadows: {
    small: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.1,
      shadowRadius: 4,
      elevation: 2,
    },
    medium: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 4 },
      shadowOpacity: 0.15,
      shadowRadius: 8,
      elevation: 4,
    },
    large: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 8 },
      shadowOpacity: 0.2,
      shadowRadius: 16,
      elevation: 8,
    },
  },
};

// Component-specific theme extensions
export const ComponentThemes = {
  // Button styles with game-like feel
  button: {
    primary: {
      backgroundColor: RodRoyaleTheme.colors.secondary, // Mustard yellow
      borderColor: RodRoyaleTheme.colors.primaryDark,
      borderWidth: 2,
      borderRadius: RodRoyaleTheme.borderRadius.md,
      ...RodRoyaleTheme.shadows.medium,
    },
    secondary: {
      backgroundColor: RodRoyaleTheme.colors.primary, // Deep blue
      borderColor: RodRoyaleTheme.colors.primaryDark,
      borderWidth: 2,
      borderRadius: RodRoyaleTheme.borderRadius.md,
      ...RodRoyaleTheme.shadows.medium,
    },
    competitive: {
      backgroundColor: RodRoyaleTheme.colors.success, // Forest green
      borderColor: RodRoyaleTheme.colors.primaryDark,
      borderWidth: 3,
      borderRadius: RodRoyaleTheme.borderRadius.lg,
      ...RodRoyaleTheme.shadows.large,
    },
  },
  
  // Card styles with battle royale feel
  card: {
    default: {
      backgroundColor: RodRoyaleTheme.colors.surface,
      borderColor: RodRoyaleTheme.colors.primary,
      borderWidth: 2,
      borderRadius: RodRoyaleTheme.borderRadius.lg,
      ...RodRoyaleTheme.shadows.medium,
    },
    competitive: {
      backgroundColor: RodRoyaleTheme.colors.surface,
      borderColor: RodRoyaleTheme.colors.secondary,
      borderWidth: 3,
      borderRadius: RodRoyaleTheme.borderRadius.lg,
      ...RodRoyaleTheme.shadows.large,
    },
    winner: {
      backgroundColor: RodRoyaleTheme.colors.successLight,
      borderColor: RodRoyaleTheme.colors.success,
      borderWidth: 3,
      borderRadius: RodRoyaleTheme.borderRadius.lg,
      ...RodRoyaleTheme.shadows.large,
    },
  },
  
  // Tab bar with competitive feel
  tabBar: {
    backgroundColor: RodRoyaleTheme.colors.surface,
    borderTopColor: RodRoyaleTheme.colors.primary,
    borderTopWidth: 3,
    ...RodRoyaleTheme.shadows.medium,
  },
};

export default RodRoyaleTheme;
