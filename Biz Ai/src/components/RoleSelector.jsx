import React from 'react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

const RoleSelector = ({ currentRole, onRoleChange }) => {
  const roles = [
    'Supervisor',
    'RFQ Processor',
    'Quotation Processor',
    'Operations',
    'Finance',
  ];

  return (
    <Select onValueChange={onRoleChange} defaultValue={currentRole}>
      <SelectTrigger className="w-[180px]">
        <SelectValue placeholder="Select role" />
      </SelectTrigger>
      <SelectContent>
        {roles.map((role) => (
          <SelectItem key={role} value={role.toLowerCase()}>
            {role}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
};

export default RoleSelector; 