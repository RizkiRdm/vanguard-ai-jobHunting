export const Skeleton = ({ className }: { className?: string }) => <div className={`bg-elevated animate-pulse rounded-md ${className || ''}`} />;
export const SkeletonCard = () => <Skeleton className="h-28 w-full" />;
export const SkeletonRow = () => <Skeleton className="h-12 w-full" />;
