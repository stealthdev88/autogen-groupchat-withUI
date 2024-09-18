import { useEffect } from 'react';
import {useState, Fragment} from 'react';
import Paper from '@mui/material/Paper';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import SendIcon from '@mui/icons-material/Send';
import InputBase from '@mui/material/InputBase';
import Divider from '@mui/material/Divider';
import Box from '@mui/material/Box';
import IconButton from '@mui/material/IconButton';
import { useBoundStore } from '../../../stores';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import Snackbar from '@mui/material/Snackbar';
import Alert from '@mui/material/Alert';
import CircularProgress from '@mui/material/CircularProgress';

function CustomizedInputBase() {
    const sendChatMessageAsync = useBoundStore((state) => state.sendChatMessageAsync)
    const pendingResponse = useBoundStore((state) => state.pendingResponse)
    const initChatWebSocket = useBoundStore((state) => state.initChatWebSocket)
    const currWebSocket = useBoundStore((state) => state.currWebSocket)
    const [message, setMessage] = useState('')
    const [openSnack, setOpenSnack] = useState(false)

    useEffect(() => {
        initChatWebSocket()
        return () => {
            try {
                currWebSocket.close();
            } catch (err) {
                // log
            }
        }
    }, []);

    const clickHandler = async (e) => {
        if (message.trim().length == 0)
            return 
        setMessage("")
        sendChatMessageAsync(message)

    }

    const handleKeyDown = (event) => {
        if (event.key === 'Enter') {
            clickHandler(event);
        }
    };
    const handleCloseSnack = () => {
        setOpenSnack(false);
    };

    return (
      <Paper sx={{ p: '2px 4px', display: 'flex', alignItems: 'center', width: "auto" }} >
        <InputBase 
          onChange={event=>{        
            setMessage(event.target.value)
          }}
          id="message_box"
          onKeyDown={handleKeyDown}
          value={message}
          sx={{ ml: 1, flex: 1 }}
          placeholder="Send message"
          disabled={pendingResponse}
          inputRef={(input) => {
            if(input != null) {
               input.focus();
            }
          }}
        />
        <IconButton id="send_message" disabled={pendingResponse} onClick={clickHandler} type="button" sx={{ p: '10px' }} aria-label="search">
            {!pendingResponse &&
                <SendIcon id="send_ok"/>
            }
            {pendingResponse &&
                <CircularProgress size="1rem"/>
            }
        </IconButton>
        <Divider sx={{ height: 28, m: 0.5 }} orientation="vertical" />
        <Snackbar open={openSnack} autoHideDuration={6000} onClose={handleCloseSnack} anchorOrigin={{ vertical: 'top', horizontal: 'center' }}>
            <Alert severity="error" sx={{ width: '100%' }}>
                Error sending message
            </Alert>
        </Snackbar>
      </Paper>
    );
}

const ChatDialog = () => {
    const chatMessages = useBoundStore((state) => state.chatMessages)
    return (
        <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column',   }}>
            <Box sx={{  flex: 1, display: 'flex', justifyContent:"flex-end", alignItems:"end" }} >
                <Grid container >
                    {chatMessages.map(({id, message, msg_from}) => {
                        if ( msg_from === "gpt")
                        {
                            const reply = message.split(":")
                            message = reply[1]
                            name = reply[0]
                        }
                        return (
                        <Fragment key={id}>
                            {(msg_from === "user") &&
                                <AccountCircleIcon  style={{marginTop:"10px", color:"darkgray"}}/>
                            }
                            {(msg_from === "gpt") &&
                                <div style={{borderRadius: "5px", backgroundColor: "lime", marginTop:"10px", color:"black"}}>{name}</div>
                            }
                            <Grid  item xs={11} sx={{  borderBottom:"1px solid #2222"  }}>
                                <Typography sx={{ my: 1.5, mx: 1 , whiteSpace: "pre-line"}} color="text.primary" >
                                    {message}
                                </Typography>
                            </Grid>
                        </Fragment>
                    )})}
                </Grid>
            </Box>
            <Box sx={{ p: 1, bgcolor: '#eaeff1', marginTop: "auto" }}>
                <CustomizedInputBase/>
            </Box>
        </Box>
    )
}

export default ChatDialog