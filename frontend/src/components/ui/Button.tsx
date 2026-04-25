export const Button = ({ variant = 'primary', size = 'md', disabled, onClick, children, className }: { variant?: 'primary' | 'ghost' | 'danger', size?: 'sm' | 'md', disabled?: boolean, onClick?: () => void, children: React.ReactNode, className?: string }) => {
  const base = "rounded-lg text-sm font-medium transition-colors duration-150";
  const variants = {
    primary: "bg-accent hover:bg-accent-hover text-white",
    ghost: "hover:bg-elevated text-text-secondary",
    danger: "border border-status-failed/30 text-status-failed hover:bg-status-failed/10"
  };
  const sizes = { sm: "px-3 py-1.5", md: "px-4 py-2" };
  return (
    <button disabled={disabled} onClick={onClick} className={`${base} ${variants[variant]} ${sizes[size]} ${disabled ? 'opacity-50 cursor-not-allowed' : ''} ${className || ''}`}>
      {children}
    </button>
  );
};
