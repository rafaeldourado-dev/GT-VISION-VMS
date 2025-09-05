import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { forwardRef } from 'react';

const KpiCard = forwardRef(({ title, value, icon: Icon, description, ...props }, ref) => {
    return (
        <Card ref={ref} {...props}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{title}</CardTitle>
                {Icon && <Icon className="h-4 w-4 text-muted-foreground" />}
            </CardHeader>
            <CardContent>
                <div className="text-2xl font-bold">{value}</div>
                <p className="text-xs text-muted-foreground">{description}</p>
            </CardContent>
        </Card>
    );
});

KpiCard.displayName = "KpiCard"

export default KpiCard;