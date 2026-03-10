/**
 * Centralized source icon rendering.
 * Maps source icon keys (from catalog) to display properties.
 */

interface SourceIconConfig {
  /** CSS class for SVG icons */
  svgClass?: string
  /** SVG path data for custom icons */
  svgPath?: string
  /** SVG viewBox (default: "0 0 24 24") */
  viewBox?: string
  /** Text/emoji fallback for non-SVG icons */
  text?: string
  /** CSS class for text icons */
  textClass?: string
}

const SOURCE_ICONS: Record<string, SourceIconConfig> = {
  reddit: {
    svgClass: 'text-orange-500',
    svgPath: 'M12 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0zm5.01 4.744c.688 0 1.25.561 1.25 1.249a1.25 1.25 0 0 1-2.498.056l-2.597-.547-.8 3.747c1.824.07 3.48.632 4.674 1.488.308-.309.73-.491 1.207-.491.968 0 1.754.786 1.754 1.754 0 .716-.435 1.333-1.01 1.614a3.111 3.111 0 0 1 .042.52c0 2.694-3.13 4.87-7.004 4.87-3.874 0-7.004-2.176-7.004-4.87 0-.183.015-.366.043-.534A1.748 1.748 0 0 1 4.028 12c0-.968.786-1.754 1.754-1.754.463 0 .898.196 1.207.49 1.207-.883 2.878-1.43 4.744-1.487l.885-4.182a.342.342 0 0 1 .14-.197.35.35 0 0 1 .238-.042l2.906.617a1.214 1.214 0 0 1 1.108-.701z',
  },
  hackernews: {
    text: 'Y',
    textClass: 'text-lg font-bold text-orange-400',
  },
  bluesky: {
    text: '🦋',
    textClass: 'text-lg',
  },
  indiehackers: {
    svgClass: 'text-indigo-600',
    svgPath: 'M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm0 4c1.105 0 2 .895 2 2s-.895 2-2 2-2-.895-2-2 .895-2 2-2zm0 10c-2.21 0-4-1.79-4-4s1.79-4 4-4 4 1.79 4 4-1.79 4-4 4zm6 6H6v-1.5c0-1.93 1.57-3.5 3.5-3.5h5c1.93 0 3.5 1.57 3.5 3.5V20z',
  },
}

const DEFAULT_ICON: SourceIconConfig = {
  text: '📰',
  textClass: 'text-lg',
}

export function useSourceIcons() {
  function getIconConfig(iconKey: string): SourceIconConfig {
    return SOURCE_ICONS[iconKey] || DEFAULT_ICON
  }

  function isSvgIcon(iconKey: string): boolean {
    const config = getIconConfig(iconKey)
    return !!config.svgPath
  }

  return {
    getIconConfig,
    isSvgIcon,
    SOURCE_ICONS,
    DEFAULT_ICON,
  }
}
