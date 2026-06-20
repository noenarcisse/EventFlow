export default function Logo({ size = 34 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 96 96" fill="none" xmlns="http://www.w3.org/2000/svg" aria-label="eventflow">
      <rect width="96" height="96" rx="24" fill="#6C4DF6" />
      <rect x="27" y="25" width="11" height="46" rx="5.5" fill="#fff" />
      <rect x="38" y="25" width="34" height="11" rx="5.5" fill="#fff" />
      <rect x="38" y="41" width="23" height="11" rx="5.5" fill="#fff" />
      <path d="M44 57 L58 63.5 L44 70" fill="none" stroke="#FF5B4A" strokeWidth="11" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
