
import { useState, useEffect } from 'react';
import useMediaQuery from '@mui/material/useMediaQuery';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import { useTheme } from '@mui/material/styles';
import ChatDialog from "./ChatDialog"
import { useBoundStore } from '../../../stores';

const drawerWidth = 256;

export default function Chat() {
    const theme = useTheme()
    const [mobileOpen, setMobileOpen] = useState(false);
    const isSmUp = useMediaQuery(theme.breakpoints.up('sm'));
    const clearChatMessages = useBoundStore((state) => state.clearChatMessages)

    useEffect(() => {
        clearChatMessages()
        // startChat()
    }, []);

    const handleDrawerToggle = () => {
        setMobileOpen(!mobileOpen);
    };

    return (
      <Box sx={{ display: 'flex', minHeight: '100vh' }}>
        <CssBaseline />
        <ChatDialog />
      </Box>
  );
}